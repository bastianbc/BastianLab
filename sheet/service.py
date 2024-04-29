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
    barcode = serializers.StringRelatedField()
    na_type = serializers.SerializerMethodField()
    area_type = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()
    matching_normal_sl = serializers.SerializerMethodField()
    seq_run = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()

    class Meta:
        model = SampleLib
        fields = ("id", "name",  "shear_volume",  "qpcr_conc", "barcode",
                  "na_type", "area_type", "method", "method_label",
                  "patient", "matching_normal_sl", "seq_run", "files")

    def get_files(self, obj):
        seq_files = SequencingFile.objects.filter(sequencing_file_set__sample_lib=obj)
        files = SequencingRunSerializerManual(seq_files, many=True).data
        return files

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
        # if obj.na_sl_links.first():
        #     nuc_acid = obj.na_sl_links.first().nucacid
        #     if nuc_acid.area_na_links.first():
        #         area = nuc_acid.area_na_links.first().area
        #         if area:
        #             patient = area.block.patient.pat_id
        #             return patient
        # return None

    def get_matching_normal_sl(self, obj):
        matching_normal_sl=[]
        if obj.na_sl_links.all():
            for na_sl_link in obj.na_sl_links.all():
                if na_sl_link.nucacid.area_na_links.all():
                    for area_na_link in na_sl_link.nucacid.area_na_links.all():
                        area = area_na_link.area
                        if area.name == "UndefinedArea":
                            continue
                        if area.area_type:
                            at = "Normal" if area.area_type.lower() == "normal" else "Tumor"
                            if at == "Tumor":
                                patient = area.block.patient
                                matching_normal = Areas.objects.filter(block__patient=patient, area_type="normal")
                                matching_normal_sl = SampleLib.objects.filter(na_sl_links__nucacid__area_na_links__area__in=matching_normal).values("name").distinct()
                                matching_normal_sl = SampleLibSerializerManual(matching_normal_sl, many=True).data
            return matching_normal_sl
        return None

    def get_seq_run(self, obj):
        captured_libs = CapturedLib.objects.filter(sl_cl_links__sample_lib_id=obj.id)
        sequencing_libs = SequencingLib.objects.filter(cl_seql_links__captured_lib__in=captured_libs)
        _sequencing_runs = SequencingRun.objects.filter(sequencing_libs__in=sequencing_libs).values("name").distinct()
        sequencing_runs = SequencingRunSerializerManual(_sequencing_runs, many=True).data
        return sequencing_runs


def get_sample_lib_list(request):
    ORDER_COLUMN_CHOICES = {
        "0": "id",
        "1": "patient",
        "2": "name",
        "3": "barcode",
        "4": "na_type",
        "5": "area_type",
        "6": "volume",
        "7": "conc",
        "8": "matching_normal",
        "9": "sequncing_run",
        "10": "files",
    }
    '''
    'order[0][column]': ['2'], 
    'order[0][dir]': ['asc'], 
    'start': ['40'], 
    'length': ['10'], 
    'search[value]': [''], 
    'search[regex]': ['false'],
    '''
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
        volume = 0
        conc = 0
        matching_normal_sl = ""
        seq_run = ""

    res = []

    for index, row in enumerate(data):
        print(index,row)
        report = Report()
        report.no = index + 1

        report.patient = row.patient
        report.sample_lib = row.name
        report.sex = row.sex
        report.barcode = row.barcode_name
        report.na_type = row.na_type
        report.area_type = row.area_type
        report.matching_normal_sl = row.matching_normal_sl
        report.conc = row.qpcr_conc
        report.volume = row.shear_volume
        report.seq_run = row.seq_run
        res.append(report)

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{file_name}.csv"'},
    )

    field_names = ["no", "patient", "sample_lib", "sex", "barcode", "na_type", "area_type",
                   "volume", "conc", "matching_normal_sl", "seq_run"]
    writer = csv.writer(response)
    writer.writerow(field_names)
    for item in res:
        writer.writerow([getattr(item, field) for field in field_names])
    return response
