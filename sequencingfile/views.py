import os
import json
import pandas as pd
from pathlib import Path
import re

from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required,permission_required
from django.http import JsonResponse
from django.contrib import messages
from core.decorators import permission_required_for_async
from .models import SequencingFile, SequencingFileSet
from .serializers import SequencingFileSerializer, SequencingFileSetSerializer
from .forms import SequencingFileForm, SequencingFileSetForm
from samplelib.models import *
from sequencingrun.models import *
from capturedlib.models import CapturedLib
from sequencinglib.models import SequencingLib
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.expressions import RawSQL


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
    print(result, "&"*50)
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
    except Exception as e:
        print(e)


def tempfiles(request):

    return render(request, "temp_file_list.html", locals())

def pattern(file):
    pattern = r"L\d{3}_R\d"
    match = re.search(pattern, file)

    if match:
        print(f"Match found: {match.group()}")
    else:
        print("No match found.")

def get_or_none(model_class, **kwargs):
    try:
        return model_class.objects.get(**kwargs)
    except Exception as e:
        return None

def levenshtein_similarity(sl):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT *, levenshtein(substring(name from 5), %s) as lev_distance
            FROM sample_lib
            WHERE name LIKE %s AND levenshtein(substring(name from 5), %s) <= 2
        """, ['059', 'AMLP%', '059'])
        results = cursor.fetchall()
        sample_lib_objects = SampleLib.objects.filter(name__in=[result[1] for result in results])
        return sample_lib_objects

def trigramSimilarity(sl):
    from django.contrib.postgres.search import TrigramSimilarity
    similar_records = SampleLib.objects.annotate(
        similarity=TrigramSimilarity('name', sl),
    ).filter(similarity__gt=0.1).order_by('-similarity')
    return similar_records

def _get_matched_sample_libray(file):
    match = re.search("[ATGC]{6}", file)
    sl=sl_name=None
    if match:
        sl_name = re.split(r'(?=(_[ATGC]{6}|-[ATGC]{6}))', file, 0)
        sl = get_or_none(SampleLib, name=sl_name)
    elif re.search("_S\d", file):
        sl_name = file.split("_S")[0]
        sl = get_or_none(SampleLib, name=sl_name)
        # if not sl:
        #     sl = levenshtein_similarity(sl_name)
        #     print(f"levenshtein_similarity__{sl_name}", sl)
    elif re.search(".deduplicated.realign.bam", file):
        sl_name = file.split(".")[0]
        sl = get_or_none(SampleLib, name=sl_name)
    elif file.endswith(".bam") or file.endswith(".bai"):
        sl_name = file.split(".")[0]
        sl = get_or_none(SampleLib, name=sl_name)
    elif re.search("_R", file):
        sl_name = file.split("_R")[0]
        sl = get_or_none(SampleLib, name=sl_name)

    return sl if sl else (file, sl_name)
    # else:
    #     pattern = r"((?:_L\d{3}_R\d)|(?:_L\d{3}_I\d)|(?:_R\d_\d{3}))"
    #     match = re.search(pattern, file)
    #     if match:
    #         parts = re.split(pattern, file, 1)
    #         sl = get_or_none(SampleLib,name=parts[0])



def filter_temp_directory(request):
    smb_directory = "/mnt/smb_volume"  # Replace with the actual directory path

    '''
    sudoPassword = 'Today@234'
    command = f'mkdir -p {smb_directory}/TEMP'
    p = os.system('echo %s|sudo -S %s' % (sudoPassword, command))
    '''
    #
    # temp_directory = Path(Path(smb_directory) / "BastianRaid-02" / "HiSeqData"/ "TEMP")
    #
    # for root, dirs, files in os.walk(temp_directory):
    #     d = dict([("name", files)])
    file = Path(Path(__file__).parent.parent / "uploads" / "df_fq.csv")
    df = pd.read_csv(file)
    df_shuffled = df.sample(frac=1).reset_index(drop=True)
    for index, value in enumerate(df['file']):
        # print(value)
        v = _get_matched_sample_libray(value)
        if isinstance(v, tuple):
            print(v)

    # Extract the matching part of the pattern
    # df['match'] = df['file'].str.extract(pattern)
    # df2 = df['file'].str.split(pattern, expand=True)[0]
    # for index, value in enumerate(df2):
    #     try:
    #         if ".bam" in value or '.bai' in value:
    #             match = re.search("[ATGC]{6}", value)
    #             if match:
    #                 parts = re.split(r'(?=(_[ATGC]{6}))', value, 1)
    #                 if "12_" in parts[0]:
    #                     sl = SampleLib.objects.get(name__icontains=parts[0].replace("_","-"))
    #                 elif "oniva" in parts[0]:
    #                     sl = SampleLib.objects.get(name=parts[0].replace("Boniva","Bivona"))
    #                 elif "CGH" in parts[0]:
    #                     sl = SampleLib.objects.get(name__icontains=parts[0])
    #                 elif "BB08" in parts[0]:
    #                     sl = SampleLib.objects.get(name__icontains=parts[0].replace("BB08","BB008"))
    #                 else:
    #                     sl = SampleLib.objects.get(name=parts[0].replace("BB08","BB008"))
    #                 file_set = sl.sequencing_file_sets.all()[0]
    #             # file_set = SequencingFileSet.objects.get(prefix=value.strip())
    #             # SequencingFile.objects.get_or_create(name=value, sequencing_file_set=file_set)
    #         else:
    #             match = re.search("[ATGC]{6}", value)
    #             if match:
    #                 parts = re.split(r'(?=(_[ATGC]{6}|-[ATGC]{6}))', value, 1)
    #                 if "MIN" in value:
    #                     sl = SampleLib.objects.get(name=parts[0].replace("-","_"))
    #                 elif "WTMM" in value:
    #                     sl = SampleLib.objects.get(name__icontains=parts[0])
    #                 elif re.search("WTMM\d", value):
    #                     print(parts[0])
    #                     sl = SampleLib.objects.get(name__icontains=parts[0].replace("WTMM","WTMM-"))
    #                 else:
    #                     sl = SampleLib.objects.get(name=parts[0])
    #     except ObjectDoesNotExist as e:
    #         print(value, e)
    #         # pass
    #     except Exception as e:
    #         print("@@@@@: ", e)
    #         pass
    l = [{
        "id": i,
        "seq_run": "",
        "file_name": d,
        "number_of_files": "",
        "sample_lib": "",
         } for i, d in enumerate(df_shuffled.file[:100].to_list())
    ]
    search_term = "AMPL-208"
    res = SampleLib.objects.raw(
        "SELECT * FROM sample_lib WHERE SOUNDEX(name) = SOUNDEX(%s)",
        [search_term]
    )
    print(list(res))
    result = dict()
    result['data'] = l
    # print(result,"&"*100)

    return JsonResponse(result)





