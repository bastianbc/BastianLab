import re
import time
from collections import Counter, namedtuple
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import permission_required
from .serializers import *
from sequencinglib.models import *
from .forms import *
from django.contrib import messages
from core.decorators import permission_required_for_async
from samplelib.models import SampleLib
from samplelib.serializers import SingleSampleLibSerializer
from sequencingfile.models import SequencingFile,SequencingFileSet
import sequencingrun.helper as helper
from django.core.files.base import ContentFile

@permission_required("sequencingrun.view_sequencingrun",raise_exception=True)
def sequencingruns(request):
    form = AnalysisRunForm(initial={"user":request.user})
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

def get_sequencing_files(request, id):
    sequencing_run = SequencingRun.objects.get(id=id)
    sample_libs = SampleLib.objects.filter(sl_cl_links__captured_lib__cl_seql_links__sequencing_lib__sequencing_runs=sequencing_run).distinct()
    file_sets = helper.get_file_sets()
    return JsonResponse({
        'success': True,
        "file_sets": file_sets,
        "sample_libs": SingleSampleLibSerializer(sample_libs, many=True).data,
        "sequencing_run": SingleSequencingRunSerializer(sequencing_run).data
    })

def save_sequencing_files(request, id):
    success = False
    sequencing_run = SequencingRun.objects.get(id=id)
    data = json.loads(request.POST.get('data'))
    # get posted data
    # files from source directory
    file_sets = helper.get_file_sets()

    transfers = [] # file pairs to transfer as (source,destination) construct
    #create data of the transfer files
    for d in data:
        if d["initial"] != d["swap"]:
            # files to swap
            files = [x["files"] for x in file_sets if x["file_set"] == d["initial"] or x["file_set"] == d["swap"]]
            for file_name in files[0]:
                # change file name as inserting the "FLAG" statement
                new_file_name = helper.add_flag_to_filename(file_name)
                transfers.append((file_name,new_file_name))
        else:
            files = [x["files"] for x in file_sets if x["file_set"] == d["initial"]]
            for file_name in files[0]:
                transfers.append((file_name,file_name))

    success, directory_path = helper.file_transfer(sequencing_run,transfers)

    return JsonResponse({"success": success})

def get_sample_libs_async(request):
    """
    Provides the data needed to generate an analysis sheet. Returns a list that the sequencing run and the sample libraries that belong to it.
    It can be worked on multiple sequencing runs selected by a user.
    # Parameters:
    selected_ids: List of Ids of selected and pushed sequencing runs.
    # Returns:
    A list data formatted according to purpose.
    """
    selected_ids = json.loads(request.GET.get("selected_ids"))

    data = {}

    for selected_id in selected_ids:
        sequencing_run = SequencingRun.objects.get(id=selected_id)
        sample_libs = SampleLib.objects.filter(
            sl_cl_links__captured_lib__cl_seql_links__sequencing_lib__sequencing_runs__id=selected_id
        ).distinct()

        data[sequencing_run.name] = [
            {"id": sample_lib.id, "name": sample_lib.name} for sample_lib in sample_libs
        ]

    data = {
        "seqr1":[
            {"id":1, "name":"sample_lib 1"},
            {"id":2, "name":"sample_lib 2"},
            {"id":3, "name":"sample_lib 3"},
        ],
        "seqr2":[
            {"id":4, "name":"sample_lib 4"},
            {"id":5, "name":"sample_lib 5"},
        ],
    }

    return JsonResponse(data)

def save_analysis_run(request):
    """
    """
    if request.method == "POST":
        form = AnalysisRunForm(request.POST)
        if form.is_valid():
            # Formu kaydetmeden önce instance oluştur
            analysis_run = form.save(commit=False)

            sheet_content = form.cleaned_data['sheet_content']

            # convert to csv
            csv_file = ContentFile(sheet_content.encode('utf-8'))
            file_name = f"{analysis_run.user.username}_analysis_sheet.csv"

            # Dosyayı 'sheet' alanına kaydet
            analysis_run.sheet.save(file_name, csv_file, save=False)

            # AnalysisRun instance'ını kaydet
            analysis_run.save()

            return JsonResponse({"success": True})
    return JsonResponse({"success": False})
