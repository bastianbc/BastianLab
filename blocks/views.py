from django.shortcuts import render, redirect
from .forms import *
from django.http import JsonResponse
import json
from django.contrib import messages
from lab.models import Patient
from projects.models import Project
from .serializers import BlocksSerializer, SingleBlockSerializer
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async

@permission_required_for_async("blocks.view_block")
def filter_blocks(request):
    blocks = Block.query_by_args(request.user,**request.GET)
    serializer = BlocksSerializer(blocks['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = blocks['draw']
    result['recordsTotal'] = blocks['total']
    result['recordsFiltered'] = blocks['count']
    return JsonResponse(result)

@permission_required("blocks.view_block",raise_exception=True)
def blocks(request):
    id = request.GET.get("id")
    model = request.GET.get("model")
    filter = FilterForm()
    form = AreaCreationForm()
    if model=="project" and id:
        project = Project.objects.get(id=id)
    elif model=="patient" and id:
        patient = Patient.objects.get(id=id)

    return render(request,"block_list.html",locals())

@permission_required("blocks.add_blocks",raise_exception=True)
def new_block(request):
    if request.method=="POST":
        form = BlockForm(request.POST)
        if form.is_valid():
            block = form.save()
            messages.success(request,"Block %s created successfully." % block.id)
            return redirect("blocks")
        else:
            messages.error(request,"Block not created.")
    else:
        form = BlockForm()

    return render(request,"block.html",locals())

@permission_required_for_async("blocks.add_blocks")
def add_block_to_patient_async(request):
    selected_ids = json.loads(request.GET.get("selected_ids"))
    patient_id = request.GET.get("patient_id")

    # try:
    patient = Patient.objects.get(id=patient_id)
    blocks = Block.objects.filter(id__in=selected_ids)

    for block in blocks:
        block.patient = patient
        block.save()
       
            
    # except Exception as e:
    #     return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required_for_async("blocks.change_blocks")
def remove_block_from_patient_async(request):
    selected_ids = json.loads(request.GET.get("selected_ids"))

    try:
        for id in selected_ids:
            block = Block.objects.get(bl_id=id)
            block.patient = None
            block.save()
    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required_for_async("blocks.add_blocks")
def add_block_to_project_async(request):
    selected_ids = json.loads(request.GET.get("selected_ids"))
    project_id = request.GET.get("project_id")

    try:
        project = Project.objects.get(id=project_id)
        blocks = Block.objects.filter(id__in=selected_ids)
        project.blocks.add(*blocks)
    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required_for_async("blocks.change_blocks")
def remove_block_from_project_async(request):
    selected_ids = ",".join(json.loads(request.GET.get("selected_ids")))
    project_id = request.GET.get("project_id")

    try:
        project = Project.objects.get(id=project_id)
        blocks = Block.objects.filter(id__in=selected_ids)
        project.blocks.remove(*blocks)
    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required("blocks.change_blocks",raise_exception=True)
def edit_block(request,id):
    block = Block.objects.get(id=id)

    if request.method=="POST":
        form = BlockForm(request.POST,instance=block)
        if form.is_valid():
            block = form.save()
            messages.success(request,"The block updated successfully.")
            return redirect("blocks")
        else:
            messages.error(request,"The block not updated!")
    else:
        form = BlockForm(instance=block)

    return render(request,"block.html",locals())

@permission_required_for_async("blocks.change_blocks")
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

    try:
        custom_update(Block,pk=parameters["pk"],parameters=parameters)
    except Exception as e:
        return JsonResponse({"success":False, "message": str(e)})

    return JsonResponse({"success":True})

@permission_required_for_async("blocks.delete_blocks")
def delete_block(request,id):
    try:
        block = Block.objects.get(bl_id=id)
        block.delete()
        messages.success(request,"Block %s deleted successfully." % block.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Block %s not deleted!" % block.pat_id)
        deleted = False

    return JsonResponse({ "deleted":deleted })

@permission_required("blocks.delete_blocks",raise_exception=True)
def delete_batch_blocks(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        Block.objects.filter(bl_id__in=selected_ids).delete()
    except Exception as e:
        print(str(e))
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

@permission_required_for_async("blocks.delete_blocks")
def check_can_deleted_async(request):
    id = request.GET.get("id")
    instance = Block.objects.get(bl_id=id)
    related_objects = []
    for field in instance._meta.related_objects:
        relations = getattr(instance,field.related_name)
        if relations.count() > 0:
            related_objects.append({
                "model": field.related_model.__name__,
                "count": relations.count()
            })

    return JsonResponse({"related_objects":related_objects})

def get_block_async(request):
    block = Block.objects.get(id=request.GET["id"])
    serializer = SingleBlockSerializer(block)
    return JsonResponse(serializer.data)

def export_csv_all_data(request):
    import csv
    from django.http import HttpResponse

    result = []

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="blocks.csv"'},
    )

    field_names = [f.name for f in Block._meta.fields]
    writer = csv.writer(response)
    writer.writerow(field_names)
    for patient in Block.objects.all():
        writer.writerow([getattr(patient, field) for field in field_names])

    return response

def edit_block_url(request):
    instance = BlockUrl.objects.first()
    if request.method=="POST":
        form = BlockUrlForm(request.POST,instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request,"Block URL was updated successfully")
            # return redirect('/blocks/edit_block_url')
        else:
            messages.error(request,"Block URL wasn't updated!")
    else:
        form = BlockUrlForm(instance=instance)
    return render(request,"block_url.html",locals())
