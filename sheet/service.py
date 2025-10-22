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
    patient = serializers.CharField(read_only=True)
    seq_run = serializers.SerializerMethodField()
    na_type = serializers.CharField(read_only=True)
    bait = serializers.CharField(read_only=True)
    area_type = serializers.CharField(read_only=True)
    matching_normal_sl = serializers.CharField(read_only=True)
    barcode_name = serializers.CharField(read_only=True)
    fastq = serializers.CharField(read_only=True)
    bam = serializers.CharField(read_only=True)
    bai = serializers.CharField(read_only=True)
    path_fastq = serializers.CharField(read_only=True)
    path_bam = serializers.CharField(read_only=True)
    path_bai = serializers.CharField(read_only=True)

    class Meta:
        model = SampleLib
        fields = ("id", "name", "barcode_name", "na_type", "area_type", "patient", "bait", 'fastq',
                  "bam", "bai", "path_fastq", "path_bam", "path_bai", "matching_normal_sl", "seq_run")


    # def get_patient(self, obj):
    #     _patients = Patient.objects.filter(
    #         patient_blocks__block_areas__area_na_links__nucacid__na_sl_links__sample_lib=obj
    #     ).distinct()
    #     _patients = PatientsSerializerManual(_patients, many=True).data
    #     return _patients


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

def _get_file(name):
    seq_files = SequencingFile.objects.filter(name=name).values('name', 'checksum').distinct()
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

        report.footprint = row.bait

        report.fastq = {f: _get_file(f).checksum for f in row.fastq} if row.fastq else ""
        report.path_fastq = row.path_fastq if report.fastq else ""
        if not report.fastq:
            report.bam = {f: _get_file(f).checksum for f in row.bam} if row.bam else ""
            report.bai = {f: _get_file(f).checksum for f in row.bai} if row.bai else ""
            report.path_bam = row.path_bam
            report.path_bai = row.path_bai

        report.seq_run = row.seq_run2  # ✓
        concat_files = f"{report.fastq}{report.bam}{report.bai}".replace("None","").strip()
        if not row.barcode_name or row.barcode_name == "":
            pattern = r'(?<![ACGT])[ACGT]{6,8}(?![ACGT])'
            match = re.findall(pattern, concat_files)
            if match:
                report.barcode = match[0]
        # Only add report if it hasn't been added before
        # print(report.__dict__)
        if concat_files != "":
            # seen.add(concat)
            res.append(report)
        else:
            continue
    # print(res)
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{file_name}.csv"'},
    )

    field_names = [
        "no", "patient", "sample_lib",  "barcode", "na_type",
        "area_type", "matching_normal_sl", "seq_run", "footprint",
        "fastq", "path_fastq", "bam", "path_bam", "bai", "path_bai"
    ]

    writer = csv.writer(response)
    writer.writerow(field_names)
    for item in res:
        writer.writerow([getattr(item, field) for field in field_names])
    return response


def generate_file_broad_institute(data):
    class Report(object):
        def __init__(self):
            self.no = 0
            self.sample = ""
            self.area = ""
            self.sex = ""
            self.vol_remain = ""
            self.qpcr_conc = ""
            self.block = ""
            self.area_type = ""
            self.blank = ""
            self.block_start = ""

    res = []
    for index, row in enumerate(data):
        report = Report()
        report.no = index + 1
        report.area = getattr(row, "area", "")
        report.sample = getattr(row, "name", "")
        report.block = getattr(row, "block", "")
        report.sex = getattr(row, "sex", "")
        report.area_type = getattr(row, "area_type", "")
        report.qpcr_conc = getattr(row, "qpcr_conc", "")
        report.vol_remain = getattr(row, "vol_remain", "")
        report.blank = ""
        report.block_start = "yes"
        res.append(report)

    # Create HTTP Response
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="Sequencing_sheet_for_Broad_Institute.csv"'},
    )

    # Aligned headers with your data model
    field_names = [
        "no", "sample", "area", "sex", "vol_remain",
        "qpcr_conc", "block", "area_type", "blank", "block_start"
    ]

    # Friendly column names for CSV (optional)
    display_headers = [
        "No", "Collaborator Participant ID", "Collaborator Sample ID", "Gender", "Volume", "Concentration",
        "Collaborator Sample ID_2", "Sample Type", "RIN Number", "Collected After 01/25/2015"
    ]

    writer = csv.writer(response)
    writer.writerow(display_headers)
    for item in res:
        writer.writerow([getattr(item, field) for field in field_names])

    return response


def generate_file_ucsf_cat(data):
    class Report(object):
        def __init__(self):
            self.no = 0
            self.sample = ""
            self.i7 = ""
            self.i5 = ""

    res = []
    for index, row in enumerate(data):
        report = Report()
        report.no = index + 1
        report.sample = getattr(row, "name", "")
        report.i7 = getattr(row, "i7", "")
        report.i5 = getattr(row, "i5", "")
        res.append(report)

    # Create HTTP Response
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="Sequencing_sheet_for_UCSF_CAT.csv"'},
    )

    # Aligned headers with your data model
    field_names = [
        "no", "sample", "i7", "i5"
    ]

    # Friendly column names for CSV (optional)
    display_headers = [
        "No", "Sample Name", "Index1 (i7)", "Index2 (i5)",
    ]

    writer = csv.writer(response)
    writer.writerow(display_headers)
    for item in res:
        writer.writerow([getattr(item, field) for field in field_names])

    return response
