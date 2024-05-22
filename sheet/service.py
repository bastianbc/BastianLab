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
    patient = serializers.SerializerMethodField()
    seq_run = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()
    na_type = serializers.CharField(read_only=True)
    bait = serializers.CharField(read_only=True)
    area_type = serializers.CharField(read_only=True)
    matching_normal_sl = serializers.CharField(read_only=True)
    barcode_name = serializers.CharField(read_only=True)

    class Meta:
        model = SampleLib
        fields = ("id", "name",  "shear_volume",  "qpcr_conc", "barcode_name", "bait",
                  "na_type", "area_type",
                  "patient", "matching_normal_sl", "seq_run", "file", "path")

    def get_file(self, obj):
        seq_files = SequencingFile.objects.filter(sequencing_file_set__sample_lib=obj)
        files = SequencingFileSerializerManual(seq_files, many=True).data
        return files

    def get_path(self, obj):
        return obj.sequencing_file_sets.first().path if obj.sequencing_file_sets.first() else None


    def get_patient(self, obj):
        _patients = Patients.objects.filter(
            patient_blocks__block_areas__area_na_links__nucacid__na_sl_links__sample_lib=obj
        ).distinct()
        _patients = PatientsSerializerManual(_patients, many=True).data
        return _patients

    def get_seq_run(self, obj):
        _sequencing_runs = SequencingRun.objects.filter(
            sequencing_libs__cl_seql_links__captured_lib__sl_cl_links__sample_lib=obj
        )
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

def _get_file(sl):
    seq_files = SequencingFile.objects.filter(sequencing_file_set__sample_lib=sl).values('name', 'checksum').distinct()
    file_dict = {item['name']: item['checksum'] for item in seq_files}
    return file_dict

def _get_path(sl):
    return sl.sequencing_file_sets.first().path if sl.sequencing_file_sets.first() else None


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
        seen = ""

    res = []
    seen = set()
    for index, row in enumerate(data):
        sl = SampleLib.objects.get(name=row.name)
        report = Report()

        report.no = index + 1
        report.patient = row.patient
        report.sample_lib = row.name # ✓
        report.barcode = row.barcode_name # ✓
        report.na_type = row.na_type # ✓
        report.area_type = row.area_type # ✓
        report.matching_normal_sl = row.matching_normal_sl # ✓

        report.footprint = row.bait

        if row.file:
            report.file = dict(zip(row.file, row.checksum))
            report.path = row.path
        else:
            report.file = _get_file(sl)
            report.path = _get_path(sl)
        if any([report.path == None, report.path == ""]):
            print(row.name, report.path, row.file)
        seq_run = report.path.split("/")[1] if report.path != None else ""
        report.seq_run = seq_run  # ✓

        concat = f"{row.name}_{report.seq_run}"

        # Only add report if it hasn't been added before
        if concat not in seen:
            seen.add(concat)
            res.append(report)
            print(row.name, concat, (concat in seen))
        else:
            continue

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
