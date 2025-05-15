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
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# views.py
from django.http import StreamingHttpResponse
import time, subprocess


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

def execute_mount_script():
    try:
        # Define your bash commands
        commands = [
            "sudo ufw disable",
            "sudo mount -v -t cifs //bastianlab.ucsf.edu/labshare /mnt/labshare -o credentials=/etc/smbcredentials,file_mode=0777,dir_mode=0777"
        ]

        # Execute the commands using subprocess
        for cmd in commands:
            process = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        return False



from pathlib import Path

from django.conf import settings
from sequencingfile.models import SequencingFile, SequencingFileSet

import os
import logging
from django.http import StreamingHttpResponse

ROOT_DIRS = [
    settings.SEQUENCING_FILES_SOURCE_DIRECTORY,
]

class StreamHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []

    def emit(self, record):
        message = self.format(record)
        self.logs.append(message)


# Function to stream logs to browser
def stream_sync_sequencing_files(request):
    """
    Stream the contents of a directory to the client.
    Optimized for directories with large numbers of files.

    Args:
        request: HTTP request object
        directory_path: Optional path to the directory to stream.
                       If None, uses BASE_DIR from settings.
    """
    directory_path = settings.SEQUENCING_FILES_SOURCE_DIRECTORY

    # Get optional query parameters for optimization
    batch_size = int(request.GET.get('batch_size', 100))
    max_depth = request.GET.get('max_depth')
    max_depth = int(max_depth) if max_depth else None

    def directory_generator():
        """Generator function that yields directory contents as JSON."""
        # Yield initial message
        yield f"data: {json.dumps({'type': 'info', 'message': f'Starting to scan: {directory_path}'})}\n\n"

        file_count = 0
        total_files = 0
        current_depth = 0
        file_batch = []

        try:
            # Walk the directory with topdown=True to track depth
            for root, dirs, files in os.walk(directory_path, topdown=True):
                # Calculate current depth
                rel_path = os.path.relpath(root, directory_path)
                current_depth = 0 if rel_path == '.' else rel_path.count(os.sep) + 1

                # Stop at max_depth if specified
                if max_depth is not None and current_depth > max_depth:
                    dirs[:] = []  # Clear dirs list to prevent deeper traversal
                    continue

                # Yield the current directory
                if rel_path == '.':
                    rel_path = ''

                yield f"data: {json.dumps({'type': 'directory', 'path': rel_path, 'file_count': len(files)})}\n\n"

                # Process files in batches
                for file in files:
                    file_path = os.path.join(rel_path, file)
                    full_path = os.path.join(root, file)

                    try:
                        # Use stat to get file info (faster than multiple separate calls)
                        file_stat = os.stat(full_path)
                        file_info = {
                            'type': 'file',
                            'path': file_path,
                            'size': file_stat.st_size
                        }
                        file_batch.append(file_info)
                        file_count += 1
                        total_files += 1

                        # Send batch when it reaches the batch size
                        if len(file_batch) >= batch_size:
                            yield f"data: {json.dumps({'type': 'file_batch', 'files': file_batch, 'progress': {'processed': total_files}})}\n\n"
                            file_batch = []  # Reset batch
                    except OSError:
                        yield f"data: {json.dumps({'type': 'error', 'message': f'Cannot access file: {file_path}'})}\n\n"

            # Send any remaining files in the batch
            if file_batch:
                yield f"data: {json.dumps({'type': 'file_batch', 'files': file_batch, 'progress': {'processed': total_files}})}\n\n"

            # Yield completion message
            yield f"data: {json.dumps({'type': 'info', 'message': f'Directory scan complete. Total files: {total_files}'})}\n\n"

        except PermissionError:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Permission denied accessing some directories'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Error: {str(e)}'})}\n\n"

    # Return a streaming response with SSE (Server-Sent Events) format
    response = StreamingHttpResponse(
        directory_generator(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'  # Disable buffering for Nginx
    return response


# views.py
import asyncio
from django.http import StreamingHttpResponse

async def generate_logs():
    """An example async generator that yields log lines."""
    for i in range(1, 11):
        # In real life you’d pull from your log source instead
        await asyncio.sleep(1)
        yield f"data: Log entry #{i} at {asyncio.get_event_loop().time()}\n\n"

async def stream_logs(request):
    """
    Async view that returns a streaming SSE response.
    Clients will see each line as it comes.
    """
    response = StreamingHttpResponse(
        generate_logs(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    return response


# views.py
import asyncio
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils.decorators import sync_and_async_middleware

# simple in-memory log store for demo purposes
LOG_BUFFER = []

async def generate_logs_background():
    """Populate LOG_BUFFER in the background."""
    for i in range(1, 11):
        await asyncio.sleep(1)
        LOG_BUFFER.append({
            "idx": i,
            "msg": f"Log entry #{i} at {asyncio.get_event_loop().time():.2f}"
        })

# Kick off your background task somewhere on startup:
# asyncio.create_task(generate_logs_background())

@require_GET
async def get_new_logs(request):
    """
    Query params: ?since_idx=<int>
    Returns: { logs: [ {idx, msg}, … ], last_idx: <int> }
    """
    try:
        since = int(request.GET.get("since_idx", 0))
    except ValueError:
        since = 0

    # Filter out anything with idx > since
    new = [entry for entry in LOG_BUFFER if entry["idx"] > since]
    last_idx = new[-1]["idx"] if new else since
    print(new, last_idx)
    return JsonResponse({
        "logs":   new,
        "last_idx": last_idx
    })



# asgi.py
import os, time, asyncio
from django.core.asgi import get_asgi_application
import redis.asyncio as aioredis

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
application = get_asgi_application()

# --- below, schedule the async log‐generator ---
REDIS_URL = "redis://localhost:6379/0"
LOG_KEY   = "log_buffer"

async def log_producer():
    client = aioredis.from_url(REDIS_URL)
    # generate 10 entries, one per second
    for i in range(1, 11):
        await asyncio.sleep(1)
        msg = f"Log entry #{i} at {time.time():.2f}"
        # push to Redis list
        await client.rpush(LOG_KEY, msg)

# fire-and-forget
asyncio.get_event_loop().create_task(log_producer())


async def async_view(request):
    await asyncio.sleep(2)
    data = {"message": "This is an asynchronous response."}
    return JsonResponse(data)


# yourapp/views.py

import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class LogStreamerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # launch background task to push logs
        self.log_task = asyncio.create_task(self.stream_logs())

    async def disconnect(self, close_code):
        # clean up when client disconnects
        self.log_task.cancel()

    async def stream_logs(self):
        """
        Replace this loop with reading your real log source.
        For example, tailing a file or subscribing to an external logger.
        """
        counter = 1
        try:
            while True:
                message = f"[{counter}] Example log entry"
                await self.send(text_data=message)
                counter += 1
                await asyncio.sleep(1)   # simulate delay
        except asyncio.CancelledError:
            pass  # task was cancelled on disconnect

    async def receive(self, text_data):
        # (Optional) handle messages from the client here
        pass
