from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async
from .models import SequencingFile, SequencingFileSet
from .serializers import SequencingFileSerializer, SequencingFileSetSerializer
from django.http import JsonResponse
from .forms import SequencingFileForm, SequencingFileSetForm
from django.contrib import messages
import json
from samplelib.models import *
from sequencingrun.models import *
from capturedlib.models import CapturedLib
from sequencinglib.models import SequencingLib
from pathlib import Path
import pandas as pd
from blocks.models import Blocks

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


@permission_required("sequencingfile.add_sequencingfile",raise_exception=True)
def new_sequencingfile(request):
    if request.method=="POST":
        form = SequencingFileForm(request.POST)
        if form.is_valid():
            sequencingfile = form.save()
            messages.success(request,"Sequencing File %s created successfully." % sequencingfile.name)
            return redirect("sequencingfiles")
        else:
            messages.error(request,"Sequencing File could not be created.")
    else:
        form = SequencingFileForm()

    return render(request,"sequencingfile.html",locals())

@permission_required("sequencingfile.change_sequencingfile",raise_exception=True)
def edit_sequencingfile(request,id):
    sequencingfile = SequencingFile.objects.get(file_id=id)

    if request.method=="POST":
        form = SequencingFileForm(request.POST,instance=sequencingfile)
        if form.is_valid():
            sequencingfile = form.save()
            messages.success(request,"Sequencing File %s updated successfully." % sequencingfile.name)
            return redirect("sequencingfiles")
        else:
            messages.error(request,"Sequencing File could not be updated!")
    else:
        form = SequencingFileForm(instance=sequencingfile)

    return render(request,"sequencingfile.html",locals())

@permission_required("sequencingfile.delete_sequencingfile",raise_exception=True)
def delete_sequencingfile(request,id):
    try:
        sequencingfile = SequencingFile.objects.get(file_id=id)
        sequencingfile.delete()
        messages.success(request,"Sequencing File %s deleted successfully." % sequencingfile.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Sequencing File could not be deleted!")
        deleted = False

    return JsonResponse({"deleted":deleted })

@permission_required("sequencingfile.delete_sequencingfile",raise_exception=True)
def delete_batch_sequencingfiles(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        SequencingFile.objects.filter(file_id__in=selected_ids).delete()
    except Exception as e:
        print(str(e))
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

@permission_required_for_async("sequencingfile.sequencingfile_blocks")
def check_can_deleted_async(request):
    id = request.GET.get("id")
    instance = SequencingFile.objects.get(file_id=id)
    related_objects = []
    for field in instance._meta.related_objects:
        relations = getattr(instance,field.related_name)
        if relations.count() > 0:
            related_objects.append({
                "model": field.related_model.__name__,
                "count": relations.count()
            })

    return JsonResponse({"related_objects":related_objects})


@permission_required("sequencingfileset.view_sequencingfileset",raise_exception=True)
def sequencingfilesets(request):
    return render(request, "sequencingfileset_list.html", locals())

@permission_required_for_async("sequencingfileset.view_sequencingfileset")
def filter_sequencingfilesets(request):
    sequencingfilesets = SequencingFileSet().query_by_args(request.user,**request.GET)
    serializer = SequencingFileSetSerializer(sequencingfilesets['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = sequencingfilesets['draw']
    result['recordsTotal'] = sequencingfilesets['total']
    result['recordsFiltered'] = sequencingfilesets['count']
    return JsonResponse(result)

@permission_required("sequencingfileset.add_sequencingfileset",raise_exception=True)
def new_sequencingfileset(request):
    if request.method=="POST":
        form = SequencingFileSetForm(request.POST)
        if form.is_valid():
            sequencingfileset = form.save()
            messages.success(request,"Sequencing File Set %s created successfully." % sequencingfileset.prefix)
            return redirect("sequencingfilesets")
        else:
            messages.error(request,"Sequencing File Set could not be created.")
    else:
        form = SequencingFileSetForm()

    return render(request,"sequencingfileset.html",locals())

@permission_required("sequencingfileset.change_sequencingfileset", raise_exception=True)
def edit_sequencingfileset(request,id):
    sequencingfileset = SequencingFileSet.objects.get(set_id=id)

    if request.method=="POST":
        form = SequencingFileSetForm(request.POST, instance=sequencingfileset)
        if form.is_valid():
            sequencingfileset = form.save()
            messages.success(request,"Sequencing File Set %s updated successfully." % sequencingfileset.prefix)
            return redirect("sequencingfilesets")
        else:
            messages.error(request,"Sequencing File Set could not be updated!")
    else:
        form = SequencingFileSetForm(instance=sequencingfileset)

    return render(request,"sequencingfileset.html",locals())

@permission_required("sequencingfileset.delete_sequencingfileset",raise_exception=True)
def delete_sequencingfileset(request,id):
    try:
        sequencingfileset = SequencingFileSet.objects.get(set_id=id)
        sequencingfileset.delete()
        messages.success(request,"Sequencing File Set %s deleted successfully." % sequencingfileset.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Sequencing File Set could not be deleted!")
        deleted = False

    return JsonResponse({"deleted":deleted })

@permission_required("sequencingfileset.delete_sequencingfileset",raise_exception=True)
def delete_batch_sequencingfilesets(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        SequencingFileSet.objects.filter(set_id__in=selected_ids).delete()
    except Exception as e:
        print(str(e))
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

@permission_required_for_async("sequencingfileset.sequencingfileset_blocks")
def check_can_deleted_async_set(request):
    id = request.GET.get("id")
    instance = SequencingFileSet.objects.get(set_id=id)
    related_objects = []
    for field in instance._meta.related_objects:
        relations = getattr(instance,field.related_name)
        if relations.count() > 0:
            related_objects.append({
                "model": field.related_model.__name__,
                "count": relations.count()
            })

    return JsonResponse({"related_objects":related_objects})

def make_dict(d):
    try:
        return json.loads(d)
    except:
        return None

def get_or_create_set(prefix, path, sample_lib, sequencing_run):
    if prefix:
        obj, created = SequencingFileSet.objects.get_or_create(
            prefix=prefix,
            path=path,
            sample_lib=sample_lib,
            sequencing_run=sequencing_run
        )
        return obj
    return None

def get_or_create_file(sequencing_file_set, name, checksum, type):
    if sequencing_file_set:
        obj, created = SequencingFile.objects.get_or_create(
            sequencing_file_set=sequencing_file_set,
            name=name,
            checksum=checksum,
            type=type
        )
        return obj
    return None

def get_or_create_cl(sl, name):
    if name:
        obj, created = CapturedLib.objects.get_or_create(
            name=name,
            samplelib=sl
        )
        return obj
    return None

def get_or_create_seql(cl, name):
    if name:
        obj, created = SequencingLib.objects.get_or_create(
            name=name,
            captured_lib=cl
        )
        return obj
    return None

def get_or_create_seqrun(cl, name):
    if name:
        obj, created = SequencingLib.objects.get_or_create(
            name=name,
            captured_lib=cl
        )
        return obj
    return None

def get_or_create_files_from_file(row):
    prefix = next(iter(row['fastq_file'])).split("_L0")[0]
    print(prefix)
    try:
        set_ = get_or_create_set(
            prefix=prefix,
            path=row['fastq_path'],
            sample_lib=SampleLib.objects.get(name=row["sample_lib"]),
            sequencing_run=SequencingRun.objects.get(name=row["sequencing_run"]),
        )
        for file, checksum in row["fastq_file"].items():
            get_or_create_file(
                sequencing_file_set=set_,
                name=file,
                checksum=checksum,
                type="fastq"
            )
        print("created")
    except Exception as e:
        print(e)

def get_or_create_files_from_file(row):
    prefix = next(iter(row['bam_file'])).split(".bam")[0]
    print(prefix)
    try:
        set_ = get_or_create_set(
            prefix=prefix,
            path=row['bam_bai_file_path'],
            sample_lib=SampleLib.objects.get(name=row["sample_lib"]),
            sequencing_run=SequencingRun.objects.get(name=row["sequencing_run"]),
        )
        for file, checksum in row["bam_file"].items():
            get_or_create_file(
                sequencing_file_set=set_,
                name=file,
                checksum=checksum,
                type="bam"
            )
        for file_, checksum_ in row["bam_bai_file"].items():
            get_or_create_file(
                sequencing_file_set=set_,
                name=file_,
                checksum=checksum_,
                type="bai"
            )
        print("created")
    except Exception as e:
        print(e)








