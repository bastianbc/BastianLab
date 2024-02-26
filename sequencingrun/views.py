import re
import os
import shutil
import time
from pathlib import Path
from collections import Counter
import pandas as pd
import threading

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import permission_required
from .serializers import *
from sequencinglib.models import *
from .forms import *
from django.contrib import messages
from core.decorators import permission_required_for_async
from django.conf import settings
from django.core.serializers import serialize
from samplelib.models import SampleLib
from samplelib.serializers import SingleSampleLibSerializer
from sequencingfile.models import SequencingFile,SequencingFileSet
from concurrent.futures import ThreadPoolExecutor
from utils.utils import calculate_execution_time


@permission_required("sequencingrun.view_sequencingrun",raise_exception=True)
def sequencingruns(request):
    return render(request, "sequencingrun_list.html", locals())

@permission_required_for_async("sequencingrun.view_sequencingrun")
def filter_sequencingruns(request):
    sequencingruns = SequencingRun().query_by_args(request.user,**request.GET)
    serializer = SequencingRunSerializer(sequencingruns['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = sequencingruns['draw']
    result['recordsTotal'] = sequencingruns['total']
    result['recordsFiltered'] = sequencingruns['count']

    return JsonResponse(result)

@permission_required_for_async("sequencingrun.change_sequencingrun")
def edit_sequencingrun_async(request):
    import re
    from core.utils import custom_update

    parameters = {}

    for k,v in request.POST.items():
        if k.startswith('data'):
            r = re.match(r"data\[(\d+)\]\[(\w+)\]", k)
            if r:
                parameters["pk"] = r.groups()[0]
                if v == '':
                    v = None
                parameters[r.groups()[1]] = v

    try:
        custom_update(SequencingRun,pk=parameters["pk"],parameters=parameters)
    except Exception as e:
        print(e)
        return JsonResponse({"success":False, "message": str(e)})

    return JsonResponse({"success":True})

@permission_required("sequencingrun.add_sequencingrun",raise_exception=True)
def new_sequencingrun(request):
    if request.method=="POST":
        form = SequencingRunForm(request.POST)
        if form.is_valid():
            sequencingrun = form.save()
            messages.success(request,"Sequencing Run %s created successfully." % sequencingrun.name)
            return redirect("sequencingruns")
        else:
            messages.error(request,"Sequencing Run could not be created.")
    else:
        form = SequencingRunForm()

    return render(request,"sequencingrun.html",locals())

@permission_required_for_async("sequencingrun.add_sequencingrun")
def new_sequencingrun_async(request):

    selected_ids = json.loads(request.GET.get("selected_ids"))
    options = json.loads(request.GET.get("options"))

    try:
        prefixies = SequencingRun.objects.filter(name__startswith=options["prefix"])
        autonumber = 1
        if prefixies.exists():
            max_value = max([int(p.name.split("-")[-1]) for p in prefixies])
            autonumber = max_value + 1

        sequencing_run = SequencingRun.objects.create(
            name="%s-%d" % (options["prefix"],autonumber),
            date=options["date"],
            date_run=options["date_run"],
            facility=options["facility"],
            sequencer=options["sequencer"],
            pe=options["pe"],
            amp_cycles=options["amp_cycles"],
        )

        sequencinglibs = SequencingLib.objects.filter(id__in=selected_ids)

        for sequencing_lib in sequencinglibs:
            sequencing_run.sequencing_libs.add(sequencing_lib)

    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True, "id":sequencing_run.id})

@permission_required("sequencingrun.change_sequencingrun",raise_exception=True)
def edit_sequencingrun(request,id):
    sequencing_run = SequencingRun.objects.get(id=id)

    if request.method=="POST":
        form = SequencingRunForm(request.POST,instance=sequencing_run)
        if form.is_valid():
            form.save()
            messages.success(request,"Sequencing Run %s updated successfully." % sequencing_run.name)
            return redirect("sequencingruns")
        else:
            messages.error(request,"Sequencing Run could not be updated!")
    else:
        form = SequencingRunForm(instance=sequencing_run)

    return render(request,"sequencingrun.html",locals())

@permission_required("sequencingrun.delete_sequencingrun",raise_exception=True)
def delete_sequencingrun(request,id):
    try:
        sequencing_run = SequencingRun.objects.get(id=id)
        sequencing_run.delete()
        messages.success(request,"Sequencing Run %s deleted successfully." % sequencing_run.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Sequencing Run could not be deleted!")
        deleted = False

    return JsonResponse({"deleted":deleted })

@permission_required("sequencingrun.delete_sequencingrun",raise_exception=True)
def delete_batch_sequencingruns(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        SequencingRun.objects.filter(id__in=selected_ids).delete()
    except Exception as e:
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

@permission_required("sequencingrun.view_sequencingrun",raise_exception=True)
def get_used_sequencinglibs(request,id):
    sequencing_run = SequencingRun.objects.get(id=id)
    used_sequencinglibs = sequencing_run.sequencing_libs.all()
    serializer = UsedSequencingLibSerializer(used_sequencinglibs, many=True)
    return JsonResponse(serializer.data, safe=False)

@permission_required_for_async("blocks.delete_blocks")
def check_can_deleted_async(request):
    id = request.GET.get("id")
    instance = SequencingRun.objects.get(id=id)
    related_objects = []
    for field in instance._meta.related_objects:
        relations = getattr(instance,field.related_name)
        if relations.count() > 0:
            related_objects.append({
                "model": field.related_model.__name__,
                "count": relations.count()
            })

    return JsonResponse({"related_objects":related_objects})

def get_facilities(request):
    return JsonResponse([{"label":"---------","value":""}] + [{ "label":c[1], "value":c[0] } for c in SequencingRun.FACILITY_TYPES], safe=False)

def get_sequencers(request):
    return JsonResponse([{"label":"---------","value":""}] + [{ "label":c[1], "value":c[0] } for c in SequencingRun.SEQUENCER_TYPES], safe=False)

def get_pes(request):
    return JsonResponse([{"label":"---------","value":""}] + [{ "label":c[1], "value":c[0] } for c in SequencingRun.PE_TYPES], safe=False)

def add_async(request):
    try:
        seq_run_id = request.GET["id"]
        selected_ids = json.loads(request.GET.get("selected_ids"))
        sequencing_run = SequencingRun.objects.get(id=seq_run_id)
        sequencinglibs = SequencingLib.objects.filter(id__in=selected_ids)
        for sequencing_lib in sequencinglibs:
            sequencing_run.sequencing_libs.add(sequencing_lib)
        return JsonResponse({"success":True})
    except Exception as e:
        return JsonResponse({"success":False, "message": str(e)})

def get_or_none(model_class, **kwargs):
    try:
        return model_class.objects.get(**kwargs)
    except Exception as e:
        return None


def _get_matched_sample_libray(file, sample_libs):
    match = re.search("[ATGC]{6}", file)
    sl=sl_name=None
    if match:
        sl_name = re.split(r"(?=(_[ATGC]{6}|-[ATGC]{6}))", file, maxsplit=1)[0]
        sl = sample_libs.filter(name__iexact=sl_name).first()

    elif re.search("_S\d", file):
        sl_name = file.split("_S")[0]
        sl = sample_libs.filter(name__iexact=sl_name).first()
    elif re.search(".deduplicated.realign.bam", file):
        sl_name = file.split(".")[0]
        sl = sample_libs.filter(name__iexact=sl_name).first()
    elif file.endswith(".bam") or file.endswith(".bai"):
        sl_name = file.split(".")[0]
        sl = sample_libs.filter(name__iexact=sl_name).first()
    elif re.search("_R", file):
        sl_name = file.split("_R")[0]
        sl = sample_libs.filter(name__iexact=sl_name).first()
    return sl.id if sl else None


def split_prefix(file):
    file = file.replace(".deduplicated.realign","")
    pattern = "(.*[ATGC]{6})"
    result = re.match(pattern, file)
    if result:
        prefix = result.group(1)
    elif "fastq" in file:
        prefix = (file.split("_L0")[0] if "_L0" in file
          else file.split("_00")[0] if "_00" in file
          else file.split("_R")[0] if "_R" in file and "_L0" not in file and "_00" not in file
          else None)
    elif ".bam.bai" in file:
        prefix = file.split(".bam.bai")[0]
    elif file.endswith(".bam"):
        prefix = file.split(".bam")[0]
    elif file.endswith(".bai"):
        prefix = file.split(".bai")[0]
    prefix = file.split("_L0")[0] if "_L0" in file else prefix
    return prefix


def count_file_set(file, prefix_list):
    for prefix, f in prefix_list:
        if f == file:
            counter = Counter(prefix for prefix,f in prefix_list)
            return counter[prefix]

# def load_df_fq():
#     file = Path(Path(__file__).parent.parent / "uploads" / "df_fq.csv")
#     df = pd.read_csv(file)
#
#     def merge_files(files):
#         return list(files)
#
#     # Split the 'path' column and extract the second element
#     df['group'] = df['path'].str.split('/').str[1]
#
#     # Group by the 'group' column and aggregate the 'file' column using the custom function
#     result = df.groupby('group')['file'].agg(merge_files).reset_index()
#     # print(result[result["group"]=="AGEX-02"])
#
#     return result[result["group"]=="Nimblegen10_BB13"]

def get_total_file_size(directory):
    total_size = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.stat(file_path).st_size / (1024 * 1024 * 1024)
    return total_size

def get_sequencing_files(request, id):
    try:
        sequencing_run = SequencingRun.objects.get(id=id)
        sample_libs = SampleLib.objects.filter(sl_cl_links__captured_lib__cl_seql_links__sequencing_lib__sequencing_runs=sequencing_run).distinct()
        files = os.listdir(os.path.join(settings.SEQUENCING_FILES_DIRECTORY,"TEMP"))
        prefix_list = [(split_prefix(file), file) for file in files]
        files_list = [( file, _get_matched_sample_libray(file, sample_libs), split_prefix(file), count_file_set(file, prefix_list)) for file in files]
        if len(files_list) == 0:
            return JsonResponse({'success': False, "message": 'There is no file in TEMP directory'}, status=400)  # Or any other appropriate status code
        return JsonResponse({
            'success': True,
            "files": files_list,
            "sample_libs": SingleSampleLibSerializer(sample_libs, many=True).data,
            "sequencing_run": SingleSequencingRunSerializer(sequencing_run).data
        }, status=200)
    except Exception as e:
        return JsonResponse({'success': False, "message": str(e)}, status=400)


def get_file_type(file):
    if "fastq" in file:
        return "fastq"
    elif ".bam.bai" in file:
        return "bai"
    elif ".bam" in file:
        return "bam"
    elif ".bai" in file:
        return "bai"
    return ""


def create_objects(row, seq_run):
    try:
        file_name = row["file_name"].strip()
        sample_lib = SampleLib.objects.get(id=row["sample_lib_id"])
        file_set = get_or_none(SequencingFileSet, prefix=row["file_set_name"].strip())
        if not file_set:
            file_set = SequencingFileSet.objects.create(
                prefix=row["file_set_name"].strip(),
                sequencing_run= seq_run,
                sample_lib= sample_lib,
                path= f"BastianRaid-02/FD/{seq_run.name}"
            )
        else:
            file_set.sequencing_run = seq_run
            file_set.sample_lib = sample_lib
            file_set.path = f"BastianRaid-02/FD/{seq_run.name}"
            file_set.save()


        file = get_or_none(SequencingFile, name=file_name)
        if not file:
            file = SequencingFile.objects.create(
                name=file_name,
                sequencing_file_set=file_set,
                type=get_file_type(file_name)
            )
        else:
            file.sequencing_file_set = file_set
            file.type = get_file_type(file_name)
            file.save()
    except Exception as e:
        print(e)

@calculate_execution_time
def save_sequencing_files(request):
    try:
        lock = threading.Lock()
        data = json.loads(request.POST['data'])
        for row in data:
            if row["sample_lib_id"] == "not_matched":
                return JsonResponse({"success": False, "message": "Not matched files found! Please Check the Sample Libraries."})
        seq_run = SequencingRun.objects.get(id=json.loads(request.POST['id']))
        # print("*"*100)
        # print(request.POST['id'])
        # print(seq_run)

        for row in data:
            create_objects(row, seq_run)
        source_dir = os.path.join(settings.SEQUENCING_FILES_DIRECTORY,"TEMP")
        # with lock:
        os.makedirs(os.path.join(settings.SEQUENCING_FILES_DIRECTORY, f"FD/{seq_run.name}"), exist_ok=True)
        time.sleep(2)
        destination_dir = os.path.join(settings.SEQUENCING_FILES_DIRECTORY, f"FD/{seq_run.name}")
        # with ThreadPoolExecutor(max_workers=2) as executor:
        for filename in os.listdir(source_dir):
            source_file = os.path.join(source_dir, filename)
            destination_file = os.path.join(destination_dir, filename)
            print("source_file: %s destination_file: %s" %(source_file, destination_file))
            shutil.move(source_file, destination_file)
            # executor.submit(shutil.move(source_file, destination_file))
        return JsonResponse({"success": True})
    except Exception as e:
        print(e)
        return JsonResponse({"success":False, "message": str(e)})


