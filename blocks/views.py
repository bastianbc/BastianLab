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
from variant.models import VariantCall
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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

    try:
        patient = Patient.objects.get(id=patient_id)
        blocks = Block.objects.filter(id__in=selected_ids)

        for block in blocks:
            block.patient = patient
            block.save()


    except Exception as e:
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required_for_async("blocks.change_blocks")
def remove_block_from_patient_async(request):
    selected_ids = json.loads(request.GET.get("selected_ids"))

    try:
        for id in selected_ids:
            block = Block.objects.get(id=id)
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
    """
    Asynchronously remove blocks from a project.

    Args:
        request: HTTP request containing project_id and selected_ids parameters

    Returns:
        JsonResponse with success status and optional error message
    """
    try:
        # Validate input parameters
        if not request.GET.get("selected_ids") or not request.GET.get("project_id"):
            return JsonResponse({"success": False, "error": "Missing required parameters"}, status=400)

        # Parse selected IDs safely
        try:
            selected_ids = json.loads(request.GET.get("selected_ids"))
            if not isinstance(selected_ids, list):
                return JsonResponse({"success": False, "error": "selected_ids must be a list"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON format for selected_ids"}, status=400)

        project_id = request.GET.get("project_id")

        # Get project or return 404 response
        project = Project.objects.get(id=project_id)

        # The original code used a comma-joined string for the ids, but we should use the list directly
        blocks = Block.objects.filter(id__in=selected_ids)

        project.blocks.remove(*blocks)

        return JsonResponse({"success": True})

    except ValidationError as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    except Exception as e:
        # Log the error for server-side debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error removing blocks from project: {str(e)}")

        return JsonResponse({"success": False, "error": "Server error occurred"}, status=500)

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
        block = Block.objects.get(id=id)
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
        Block.objects.filter(id__in=selected_ids).delete()
    except Exception as e:
        print(str(e))
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

@permission_required_for_async("blocks.delete_blocks")
def check_can_deleted_async(request):
    id = request.GET.get("id")
    instance = Block.objects.get(id=id)
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

def get_block_vaiants(request):
    block = Block.objects.get(id=request.GET.get('id'))
    area = block.block_areas.first()
    analyses = VariantCall.objects.filter(
        sample_lib__na_sl_links__nucacid__area_na_links__area__block=block
    ).select_related('analysis_run').distinct('analysis_run').values(
        'analysis_run_id', 'analysis_run__name'
    )
    response_data = {
        'area': {
            'id': area.id,
            'name': area.name,
            'he_image': area.image.url if area.image else None,
        },
        'block': {
            'id': block.id if block else '',
            'name': block.name if block else '',
            'body_site': block.body_site.name if block and block.body_site else '',
            'diagnosis': block.diagnosis if block and block.diagnosis else '',
            'he_image': area.image.url if area.image else None,
            'scan_number': block.scan_number if block else None,
            'block_url': block.get_block_url()
        },
        'analyses': [
            {
                'analysis_id': analysis['analysis_run_id'],
                'analysis_name': analysis['analysis_run__name']
            }
            for analysis in analyses
        ]
    }
    return JsonResponse(response_data)

def get_block_areas(request, id):
    """
    It brings the structural information of the block and the areas belonging to this block.
    """
    try:
        block = Block.objects.get(id=id)

        areas = Area.objects.filter(block_id=block_id)

        result = {
            'block_id': block.id,
            'block_name': block.name,
            'diagnosis': block.diagnosis,
            'body_site': block.body_site,
            'patient_id': block.pat_id,
            'areas': list(areas.values('area_id', 'area_name', 'area_type_id'))
        }

        return JsonResponse(result)
    except Block.DoesNotExist:
        return JsonResponse({'error': 'Blok bulunamadı'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
