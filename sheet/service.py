from samplelib.models import SampleLib
from rest_framework import serializers
from areas.models import Areas
import csv
from django.http import HttpResponse
from sequencingrun.models import SequencingRun
from capturedlib.models import CapturedLib
from sequencinglib.models import SequencingLib
from sequencingfile.models import SequencingFile,SequencingFileSet
from lab.models import Patients
from bait.serializers import BaitSerializer
from bait.models import Bait

class SequencingFileSetSerializerManual(serializers.ModelSerializer):
    class Meta:
        model = SequencingFileSet
        fields = "__all__"

class SequencingRunSerializerManual(serializers.ModelSerializer):
    class Meta:
        model = SequencingRun
        fields = ("name",)

class SampleLibSerializerManual(serializers.ModelSerializer):
    class Meta:
        model = SampleLib
        fields = "__all__"

class SequencingFileSerializerManual(serializers.ModelSerializer):
    class Meta:
        model = SequencingFile
        fields = "__all__"

class PatientsSerializerManual(serializers.ModelSerializer):
    class Meta:
        model = Patients
        fields = '__all__'

class CustomSampleLibSerializer(serializers.ModelSerializer):
    method_label = serializers.SerializerMethodField()
    barcode = serializers.SerializerMethodField()
    bait = serializers.SerializerMethodField()
    na_type = serializers.SerializerMethodField()
    area_type = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()
    matching_normal_sl = serializers.SerializerMethodField()
    seq_run = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()

    class Meta:
        model = SampleLib
        fields = ("id", "name",  "shear_volume",  "qpcr_conc", "barcode", "bait",
                  "na_type", "area_type", "method", "method_label",
                  "patient", "matching_normal_sl", "seq_run", "file", "path")

    def get_bait(self, obj):
        baits = Bait.objects.filter(captured_libs__sl_cl_links__sample_lib=obj).distinct()
        bait = BaitSerializer(baits, many=True).data
        return bait if bait else None

    def get_barcode(self,obj):
        barcode = obj.barcode
        return obj.barcode.i5 or obj.barcode.i7 if barcode else None

    def get_file(self, obj):
        seq_files = SequencingFile.objects.filter(sequencing_file_set__sample_lib=obj)
        files = SequencingFileSerializerManual(seq_files, many=True).data
        return files

    def get_path(self, obj):
        return obj.sequencing_file_sets.first().path if obj.sequencing_file_sets.first() else None

    def get_method_label(self,obj):
        return obj.method.name if obj.method else None

    def get_na_type(self, obj):
        return obj.na_sl_links.first().nucacid.na_type if len(obj.na_sl_links.all())>0 else None

    def get_area_type(self, obj):
        area_type=[]
        if obj.na_sl_links.all():
            for na_sl_link in obj.na_sl_links.all():
                if na_sl_link.nucacid.area_na_links.all():
                    for area_na_link in na_sl_link.nucacid.area_na_links.all():
                        area = area_na_link.area
                        if area.name == "UndefinedArea":
                            continue
                        if area.area_type:
                            at = "Normal" if area.area_type.lower() == "normal" else "Tumor"
                            if at not in area_type:
                                area_type.append(at)
        return area_type

    def get_patient(self, obj):
        _patients = Patients.objects.filter(
            patient_blocks__block_areas__area_na_links__nucacid__na_sl_links__sample_lib=obj
        ).distinct()
        _patients = PatientsSerializerManual(_patients, many=True).data
        return _patients


    def get_matching_normal_sl(self, obj):
        matching_normal_sl=[]
        if obj.na_sl_links.all():
            for na_sl_link in obj.na_sl_links.all():
                if na_sl_link.nucacid.area_na_links.all():
                    for area_na_link in na_sl_link.nucacid.area_na_links.all():
                        area = area_na_link.area
                        if area.area_type:
                            at = "Normal" if area.area_type.lower() == "normal" else "Tumor"
                            if at == "Tumor":
                                patient = area.block.patient
                                matching_normal = Areas.objects.filter(block__patient=patient, area_type="normal")
                                matching_normal_sl = SampleLib.objects.filter(na_sl_links__nucacid__area_na_links__area__in=matching_normal).values("name").distinct()
                                matching_normal_sl = SampleLibSerializerManual(matching_normal_sl, many=True).data

            return matching_normal_sl if len(matching_normal_sl) < 4 else None

        return None

    def get_seq_run(self, obj):
        captured_libs = CapturedLib.objects.filter(sl_cl_links__sample_lib_id=obj.id)
        sequencing_libs = SequencingLib.objects.filter(cl_seql_links__captured_lib__in=captured_libs)
        _sequencing_runs = SequencingRun.objects.filter(sequencing_libs__in=sequencing_libs).values("name").distinct()
        sequencing_runs = SequencingRunSerializerManual(_sequencing_runs, many=True).data
        return sequencing_runs


def get_sample_lib_list(request):
    mutable_querydict = request.GET.copy()
    mutable_querydict['order[0][column]'] = '1'
    mutable_querydict['order[0][dir]'] = 'asc'
    samplelibs = SampleLib.query_by_args(
        **mutable_querydict,
        user=request.user,
        order_column="name",
        order="asc",
        sequencing_run=[False],
        barcode=[False],
        i5=[False],
        i7=[False],
        area_type=[False],
        bait=[False])

    serializer = CustomSampleLibSerializer(samplelibs['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    return result


def generate_file(data, file_name):
    class Report(object):
        no = 0
        patient = ""
        sample_lib = ""
        barcode = ""
        na_type = ""
        area_type = ""
        matching_normal_sl = ""
        seq_run = ""
        footprint = ""

    res = []

    for index, row in enumerate(data):
        print(row.__dict__)
        report = Report()
        report.no = index + 1
        files = dict(zip(row.file, row.checksum))
        report.patient = row.patient
        report.sample_lib = row.name # ✓
        report.barcode = row.barcode_name # ✓
        report.na_type = row.na_type # ✓
        report.area_type = row.area_type # ✓
        report.matching_normal_sl = row.matching_normal_sl # ✓
        row.path = None if row.path == 'nan' else row.path
        seq_run = row.path.split("/")[1] if row.path != None else ""
        report.seq_run = seq_run # ✓
        # print(row.file, row.file, row.path, row.name)
        report.file = files
        report.footprint = row.bait
        report.path = row.path
        # print(row.bait)
        res.append(report)

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{file_name}.csv"'},
    )

    field_names = ["no", "patient", "sample_lib",  "barcode", "na_type", "area_type",
                   "matching_normal_sl", "seq_run", "footprint", "file", "path"]

    writer = csv.writer(response)
    writer.writerow(field_names)
    for item in res:
        writer.writerow([getattr(item, field) for field in field_names])
    return response
