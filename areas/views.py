from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.http import JsonResponse
import json
from django.contrib import messages
from blocks.models import *
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async

@permission_required_for_async("areas.view_areas")
def filter_areas(request):
    from .serializers import AreasSerializer

    areas = Areas().query_by_args(request.user,**request.GET)
    serializer = AreasSerializer(areas['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = areas['draw']
    result['recordsTotal'] = areas['total']
    result['recordsFiltered'] = areas['count']

    return JsonResponse(result)

@permission_required("areas.view_areas",raise_exception=True)
def areas(request):
    form = ExtractionOptionsForm()
    return render(request,"area_list.html",locals())

@permission_required("areas.add_areas",raise_exception=True)
def new_area(request):
    if request.method=="POST":
        form = AreaForm(request.POST)
        if form.is_valid():
            try:
                area = form.save()
                messages.success(request,"Area %s was created successfully." % area.ar_id)
                return redirect("areas")
            except Exception as e:
                messages.error(request,"Area wasn't created. %s" % str(e))
        else:
            messages.error(request,"Area wasn't created.")
    else:
        form = AreaForm()

    return render(request,"area.html",locals())

@permission_required("areas.add_areas",raise_exception=True)
def add_area_to_block_async(request):
    block_id = json.loads(request.GET.get("block_id"))
    options = json.loads(request.GET.get("options"))

    try:
        for _ in range(int(options["number"])):
            block = Blocks.objects.get(bl_id=block_id)
            Areas.objects.create(
                block=block,
            )

    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required("areas.change_areas",raise_exception=True)
def edit_area(request,id):
    area = Areas.objects.get(ar_id=id)

    if request.method=="POST":
        form = AreaForm(request.POST,instance=area)
        if form.is_valid():
            area = form.save()
            messages.success(request,"Area %s was updated successfully." % area.ar_id)
            return redirect("areas")
        else:
            messages.error(request,"Area wasn't updated!")
    else:
        form = AreaForm(instance=area)

    return render(request,"area.html",locals())

@permission_required("areas.change_areas",raise_exception=True)
def edit_area_async(request):
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
        custom_update(Areas,pk=parameters["pk"],parameters=parameters)
    except Exception as e:
        return JsonResponse({"success":False, "message": str(e)})

    return JsonResponse({"success":True})

@permission_required("areas.delete_areas",raise_exception=True)
def delete_area(request,id):
    try:
        area = Areas.objects.get(ar_id=id)
        area.delete()
        messages.success(request,"Area %s was deleted successfully." % area.ar_id)
        deleted = True
    except Exception as e:
        messages.error(request, "Area %s wasn't deleted!" % area.ar_id)
        deleted = False

    return JsonResponse({ "deleted":True })

@permission_required("areas.delete_areas",raise_exception=True)
def delete_batch_areas(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        Areas.objects.filter(ar_id__in=selected_ids).delete()
    except Exception as e:
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

def get_collections(request):
    return JsonResponse(Areas.get_collections(), safe=False)

def get_area_types(request):
    return JsonResponse(Areas.get_area_types(), safe=False)

@permission_required_for_async("blocks.delete_blocks")
def check_can_deleted_async(request):
    id = request.GET.get("id")
    instance = Areas.objects.get(ar_id=id)
    related_objects = []
    for field in instance._meta.related_objects:
        relations = getattr(instance,field.related_name)
        if relations.count() > 0:
            related_objects.append({
                "model": field.related_model.__name__,
                "count": relations.count()
            })

    return JsonResponse({"related_objects":related_objects})
