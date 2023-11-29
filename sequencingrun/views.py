from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required,permission_required
from .serializers import *
from .models import *
from sequencinglib.models import *
from .forms import *
from django.contrib import messages
from capturedlib.models import *
from core.decorators import permission_required_for_async
from pathlib import Path
import pandas as pd


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

    return JsonResponse({"success":True})

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

def get_or_create_files_from_file(row):
    print()


def _create_file_from_file():
    file = Path(Path(__file__).parent.parent / "uploads" / "Sample Library with grid view, analysis view and more-Grid view-7.csv")
    df = pd.read_csv(file)
    # print(df.columns)
    # df['fastq_file'] = df['fastq_file'].str.replace('"', "'").str.replace("'", '"')
    # df["fastq_file"] = df["fastq_file"].astype('str')
    # df["fastq_file"] = df["fastq_file"].apply(lambda x: make_dict(x))

    df[~df["fastq_file"].isnull()].apply(lambda row: get_or_create_files_from_file(row), axis=1)

