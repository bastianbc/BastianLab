from samplelib.models import SampleLib
from rest_framework import serializers
import csv
from django.db.models import OuterRef, Exists
from django.http import HttpResponse
from sequencingrun.models import SequencingRun
from sequencingfile.models import SequencingFile,SequencingFileSet
from lab.models import Patient
import json
import re
from barcodeset.models import Barcode
from django.db.models import Q


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
        model = Patient
        fields = '__all__'

class CustomSampleLibSerializer(serializers.ModelSerializer):
    patient = serializers.SerializerMethodField()
    seq_run = serializers.SerializerMethodField()
    # file = serializers.SerializerMethodField()
    file_set = serializers.SerializerMethodField()
    # path = serializers.SerializerMethodField()
    na_type = serializers.CharField(read_only=True)
    bait = serializers.CharField(read_only=True)
    area_type = serializers.CharField(read_only=True)
    matching_normal_sl = serializers.CharField(read_only=True)
    barcode_name = serializers.CharField(read_only=True)
    fastq = serializers.CharField(read_only=True)
    file = serializers.CharField(read_only=True)
    bam = serializers.SerializerMethodField()
    bai = serializers.SerializerMethodField()
    path_fastq = serializers.SerializerMethodField()
    path_bam = serializers.SerializerMethodField()
    path_bai = serializers.SerializerMethodField()

    class Meta:
        model = SampleLib
        fields = ("id", "name", "barcode_name",
                  "na_type", "area_type", "patient", "bait", 'fastq',
                  "bam", "bai", "file",
                  "path_fastq", "path_bam", "path_bai",
                  "matching_normal_sl", "seq_run",  "file_set")

    # def get_fastq(self, obj):
    #     seq_files = SequencingFile.objects.filter(sequencing_file_set__sample_lib=obj, type='fastq')
    #     if seq_files:
    #         files = SequencingFileSerializerManual(seq_files, many=True).data
    #         file_dict = {file['name']: file['checksum'] for file in files}
    #         return json.dumps(file_dict)
    #     return

    def get_bam(self, obj):
        seq_files = SequencingFile.objects.filter(sequencing_file_set__sample_lib=obj, type='bam')
        if seq_files:
            files = SequencingFileSerializerManual(seq_files, many=True).data
            file_dict = {file['name']: file['checksum'] for file in files}
            return json.dumps(file_dict)
        return

    def get_bai(self, obj):
        seq_files = SequencingFile.objects.filter(sequencing_file_set__sample_lib=obj, type='bai')
        if seq_files:
            files = SequencingFileSerializerManual(seq_files, many=True).data
            file_dict = {file['name']: file['checksum'] for file in files}
            return json.dumps(file_dict)
        return

    # def get_file(self, obj):
    #     seq_files = SequencingFile.objects.filter(sequencing_file_set__sample_lib=obj)
    #     files = SequencingFileSerializerManual(seq_files, many=True).data
    #     file_dict = {file['name']: file['checksum'] for file in files}
    #     return json.dumps(file_dict)

    def get_file_set(self, obj):
        seq_files = SequencingFileSet.objects.filter(sample_lib=obj)
        files = SequencingFileSetSerializerManual(seq_files, many=True).data
        return files

    def get_path_fastq(self, obj):
        return obj.sequencing_file_sets.filter(sequencing_files__type='fastq')[0].path if obj.sequencing_file_sets.filter(sequencing_files__type='fastq') else None

    def get_path_bam(self, obj):
        return obj.sequencing_file_sets.filter(sequencing_files__type='bam')[0].path if obj.sequencing_file_sets.filter(sequencing_files__type='bam') else None

    def get_path_bai(self, obj):
        return obj.sequencing_file_sets.filter(sequencing_files__type='bai')[0].path if obj.sequencing_file_sets.filter(sequencing_files__type='bai') else None


    def get_patient(self, obj):
        _patients = Patient.objects.filter(
            patient_blocks__block_areas__area_na_links__nucacid__na_sl_links__sample_lib=obj
        ).distinct()
        _patients = PatientsSerializerManual(_patients, many=True).data
        return _patients

    # def get_seq_run(self, obj):
    #     _sequencing_runs = SequencingRun.objects.filter(
    #         sequencing_libs__cl_seql_links__captured_lib__sl_cl_links__sample_lib=obj
    #     )
    #     sequencing_runs = SequencingRunSerializerManual(_sequencing_runs, many=True).data
    #     return sequencing_runs

    def get_seq_run(self, obj):
        try:
            seq_run = SequencingRun.objects.get(id=obj.seq_run)
            return seq_run.name
        except SequencingRun.DoesNotExist:
            return None


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

def _get_file(file):
    try:
        return SequencingFile.objects.get(name=file)
    except:
        return

def _get_files(sample_lib, sequencing_run):
    try:
        return SequencingFile.objects.filter(sequencing_file_set__sample_lib__name=sample_lib,
                                             sequencing_file_set__sequencing_run__id=sequencing_run).order_by('-type')
    except:
        return

def _seq_run(path):
    try:
        return path.split("/")[1]
    except:
        return

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
        fastq = ""
        bam = ""
        bai = ""
        path_fastq = ""
        path_bam = ""
        path_bai = ""

    res = []
    seen = []
    for index, row in enumerate(data):
        sl = SampleLib.objects.get(name=row.name)
        sl_seq_run = f"{sl.name}-{row.seq_run}"
        if sl_seq_run not in seen:
            seen.append(sl_seq_run)
        else:
            continue
        report = Report()
        report.no = index + 1
        report.patient = row.patient
        report.sample_lib = row.name.strip().replace(" ", "_") # ✓
        report.barcode = row.barcode_name # ✓

        report.na_type = row.na_type # ✓
        report.area_type = row.area_type # ✓
        report.matching_normal_sl = ''
        if row.matching_normal_sl:
            if SequencingFileSet.objects.filter(sample_lib=SampleLib.objects.get(name=row.matching_normal_sl)):
                report.matching_normal_sl = row.matching_normal_sl.replace(" ", "_") if row.matching_normal_sl else ""
        fastq, bam, bai = [], [], []
        report.footprint = row.bait
        files = _get_files(row.name, row.seq_run)
        if files:
            for file in files:
                if file.type == "fastq":
                    fastq.append(file.name)
                    report.path_fastq = row.path if row.path else ""
                    continue
                if file.type == "bam" and not report.path_fastq:
                    bam.append(file.name)
                    report.path_bam = row.path if row.path else ""
                if file.type == "bai" and not report.path_fastq:
                    bai.append(file.name)
                    report.path_bai = row.path if row.path else ""
        report.fastq = {f: _get_file(f).checksum for f in fastq} if fastq else ""
        report.bam = {f: _get_file(f).checksum for f in bam} if bam else ""
        report.bai = {f: _get_file(f).checksum for f in bai} if bai else ""
        # else:
        #     report.fastq = _get_file(sl)
        #     report.path_fastq = _get_path(sl)
        # if not report.fastq:
        #     report.fastq = _get_file(sl)
        #     report.path_fastq = _get_path(sl)
        # if report.fastq:
        #     report.bam, report.bai, report.path_bai, report.path_bam = "","","",""
        seq_run = report.path_fastq.split("/")[1] if report.path_fastq != "" and report.path_fastq != None else ""
        report.seq_run = row.seq_run2  # ✓
        concat_files = f"{report.fastq}{report.bam}{report.bai}".replace("None","").strip()
        if not row.barcode_name or row.barcode_name == "":
            pattern = r'(?<![ACGT])[ACGT]{6,8}(?![ACGT])'
            match = re.findall(pattern, concat_files)
            if match:
                report.barcode = match[0]
        # Only add report if it hasn't been added before
        if concat_files != "":
            # seen.add(concat)
            res.append(report)
        else:
            continue

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{file_name}.csv"'},
    )

    field_names = ["no", "patient", "sample_lib",  "barcode", "na_type", "area_type",
                   "matching_normal_sl", "seq_run", "footprint", "fastq", "path_fastq", "bam", "path_bam", "bai", "path_bai"]

    writer = csv.writer(response)
    writer.writerow(field_names)
    for item in res:
        writer.writerow([getattr(item, field) for field in field_names])
    return response
