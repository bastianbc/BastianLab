from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.forms.models import inlineformset_factory
from .models import Blocks
from lab.models import Patients
from .forms import BlockForm
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
import json
from django.contrib import messages
from projects.models import Projects

def filter_blocks(request):
    from .serializers import BlocksSerializer

    blocks = Blocks().query_by_args(request.user,**request.GET)
    serializer = BlocksSerializer(blocks['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = blocks['draw']
    result['recordsTotal'] = blocks['total']
    result['recordsFiltered'] = blocks['count']

    return JsonResponse(result)

def blocks(request):
    project_id = request.GET.get("project_id")
    if project_id:
        project = Projects.objects.get(pr_id=project_id)
    return render(request,"block_list.html",locals())

def new_block(request):
    if request.method=="POST":
        form = BlockForm(request.POST)
        if form.is_valid():
            block = form.save()
            messages.success(request,"Block %s was created successfully." % block.bl_id)
            return redirect("blocks")
        else:
            messages.error(request,"Block wasn't created.")
    else:
        form = BlockForm()

    return render(request,"block.html",locals())

def add_block_to_patient_async(request):
    selected_ids = json.loads(request.GET.get("selected_ids"))

    try:
        for id in selected_ids:
            patient = Patients.objects.get(pat_id=id)
            Blocks.objects.create(patient=patient)
    except Exception as e:
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

def add_block_to_project_async(request):
    selected_ids = json.loads(request.GET.get("selected_ids"))
    project_id = request.GET.get("project_id")

    try:
        for id in selected_ids:
            project = Projects.objects.get(pr_id=project_id)
            Blocks.objects.create(project=project)
    except Exception as e:
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

def edit_block(request,id):
    block = Blocks.objects.get(bl_id=id)

    if request.method=="POST":
        form = BlockForm(request.POST,instance=block)
        if form.is_valid():
            block = form.save()
            messages.success(request,"Block %s was updated successfully." % block.pat_id)
            return redirect("blocks")
        else:
            messages.error(request,"Block wasn't updated!")
    else:
        form = BlockForm(instance=block)

    return render(request,"block.html",locals())

def edit_block_async(request):
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

    custom_update(Blocks,pk=parameters["pk"],parameters=parameters)

    return JsonResponse({"result":True})

def delete_block(request,id):
    try:
        block = Blocks.objects.get(bl_id=id)
        block.delete()
        messages.success(request,"Block %s was deleted successfully." % block.pat_id)
        deleted = True
    except Exception as e:
        messages.error(request, "Block %s wasn't deleted!" % block.pat_id)
        deleted = False

    return JsonResponse({ "deleted":True })
