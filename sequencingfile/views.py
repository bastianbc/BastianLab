from django.shortcuts import render
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async
from .models import SequencingFile
from .serializers import SequencingFileSerializer
from django.http import JsonResponse
import pandas as pd
from pathlib import Path
import json
from samplelib.models import SampleLib

@permission_required("sequencingfile.view_sequencingfile",raise_exception=True)
def sequencingfiles(request):
    return render(request, "sequencingfile_list.html", locals())

@permission_required_for_async("sequencingfile.view_sequencingfile")
def filter_sequencingfiles(request):
    sequencingfiles = SequencingFile().query_by_args(request.user,**request.GET)
    serializer = SequencingFileSerializer(sequencingfiles['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = sequencingfiles['draw']
    result['recordsTotal'] = sequencingfiles['total']
    result['recordsFiltered'] = sequencingfiles['count']

    return JsonResponse(result)


def get_or_create_fastq_file(d:dict):

    SequencingFile.objects.create(
        sample_lib=d.get("sample_lib"),
        folder_name=d.get("folder_name"),
        read1_file=d.get("read1_file"),
        read1_checksum=d.get("read1_checksum"),
        read2_file=d.get("read2_file"),
        read2_checksum=d.get("read2_checksum"),
        path=d.get("fastq_path")
    )




def get_or_create_sample_lib(value):
    if value:
        obj, created = SampleLib.objects.get_or_create(
            name=value
        )
        print("created")
        return obj
    return None

def file_get_or_create_from_report(row):

    d={}
    d["read1_file"] = ""
    d["read1_checksum"] = ""
    d["read2_file"] = ""
    d["read2_checksum"] = ""
    sl = get_or_create_sample_lib(row["sample_lib"])
    d["sample_lib"]=sl
    print("SLLLL:",sl)
    for k,v in row["fastq_file"].items():
        file=k.strip()
        d["folder_name"] = row["sequencing_run"]
        if "_R1_" in file:
            d["read1_file"] = file
            d["read1_checksum"] = v if v else None
        if "_R2_" in file:
            d["read2_file"] = file
            d["read2_checksum"] = v if v else None
        d["path"] = row["fastq_path"]

        get_or_create_fastq_file(d)
        print("created")

def _cerate_files_from_consolideated_data():
    file = Path(Path(__file__).parent.parent / "uploads" / "m.csv")
    df = pd.read_csv(file)

    df['fastq_file'] = df['fastq_file'].str.replace('"', "'").str.replace("'", '"')
    df["fastq_file"] = df["fastq_file"].astype('str')

    df['bam_bai_file'] = df['bam_bai_file'].str.replace('"', "'").str.replace("'", '"')
    df["bam_bai_file"] = df["bam_bai_file"].astype('str')

    df['bam_file'] = df['bam_file'].str.replace('"', "'").str.replace("'", '"')
    df["bam_file"] = df["bam_file"].astype('str')

    def make_dict(d):
        try:
            return json.loads(d)
        except:
            return None

    df["fastq_file"] = df["fastq_file"].apply(lambda x: make_dict(x))
    df["bam_bai_file"] = df["fastq_file"].apply(lambda x: make_dict(x))
    df["bam_file"] = df["fastq_file"].apply(lambda x: make_dict(x))

    df[~pd.isnull(df["fastq_file"])].apply(lambda row: file_get_or_create_from_report(row), axis=1)
