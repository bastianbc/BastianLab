from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.http import JsonResponse
from django.contrib import messages
from blocks.models import *
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async
from .serializers import AreasSerializer
from areatype.models import AreaType
from variant.models import VariantCall
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@permission_required_for_async("areas.view_area")
def filter_areas(request):
    from django.core.mail import send_mail
    context = {
        'user': "user",
        'activation_url': "activation_url",
        'logo_url': 'https://melanomalab.ucsf.edu/static/assets/media/logos/bastianlab.png',
        'icon_url': 'https://melanomalab.ucsf.edu/static/media/email/icon-positive-vote-1.svg',
        'site_url': 'https://melanomalab.ucsf.edu',
        'welcome_message': 'Welcome to our platform!',
        'support_phone': '+31 6 3344 55 56',
        'support_email': 'melanomalab@ucsf.edu',
        'support_url': 'https://melanomalab.ucsf.edu',
    }

    html_message = render_to_string('welcome.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject='Welcome to Our Platform!',
        message=plain_message,
        from_email=None,
        recipient_list=["ceylan.bagci@ucsf.edu"],
        html_message=html_message,
    )


    areas = Area.query_by_args(request.user, **request.GET)
    serializer = AreasSerializer(areas['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = areas['draw']
    result['recordsTotal'] = areas['total']
    result['recordsFiltered'] = areas['count']

    return JsonResponse(result)

@permission_required("areas.view_area",raise_exception=True)
def areas(request):
    form = ExtractionOptionsForm()
    return render(request,"area_list.html",locals())

@permission_required("areas.add_area",raise_exception=True)
def new_area(request):
    if request.method=="POST":
        form = AreaForm(request.POST)
        if form.is_valid():
            try:
                area = form.save()
                messages.success(request,"Area %s created successfully." % area.name)
                return redirect("areas")
            except Exception as e:
                messages.error(request,"Area could not be created. %s" % str(e))
        else:
            messages.error(request,"Area could not be created.")
    else:
        form = AreaForm()

    return render(request,"area.html",locals())

@permission_required("areas.add_area",raise_exception=True)
def add_area_to_block_async(request):
    try:
        block_id = request.GET.get("block_id")
        options = request.GET.get("options")

        if not block_id or not options:
            return JsonResponse({"success": False, "error": "Missing parameters"}, status=400)

        block_id = int(block_id)
        options = json.loads(options)
        number_of_areas = int(options.get("number", 0))
        
        for _ in range(number_of_areas):
            block = Block.objects.get(id=block_id)
            Area.objects.create(
                block=block,
            )

    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required("areas.change_area",raise_exception=True)
def edit_area(request,id):
    area = Area.objects.get(id=id)

    if request.method=="POST":
        form = AreaForm(request.POST,instance=area)
        if form.is_valid():
            area = form.save()
            messages.success(request,"Area %s updated successfully." % area.name)
            return redirect("areas")
        else:
            messages.error(request,"Area could not be updated!")
    else:
        form = AreaForm(instance=area)

    return render(request,"area.html",locals())

@permission_required("areas.change_area",raise_exception=True)
def edit_area_async(request):
    import re
    from core.utils import custom_update

    parameters = {}

    for k,v in request.POST.items():
        print(k,v)
        if k.startswith('data'):
            r = re.match(r"data\[(\d+)\]\[(\w+)\]", k)
            if r:
                parameters["pk"] = r.groups()[0]
                if v == '':
                    v = None
                parameters[r.groups()[1]] = v

    try:
        custom_update(Area,pk=parameters["pk"],parameters=parameters)
    except Exception as e:
        return JsonResponse({"success":False, "message": str(e)})

    return JsonResponse({"success":True})

@permission_required("areas.delete_area",raise_exception=True)
def delete_area(request,id):
    try:
        area = Area.objects.get(id=id)
        area.delete()

        messages.success(request,"Area %s deleted successfully." % area.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Area %s could not be deleted!" % area.name)
        deleted = False

    return JsonResponse({ "deleted":True })

@permission_required("areas.delete_area",raise_exception=True)
def delete_batch_areas(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        Area.objects.filter(id__in=selected_ids).delete()
    except Exception as e:
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

@permission_required_for_async("blocks.delete_blocks")
def check_can_deleted_async(request):
    id = request.GET.get("id")
    instance = Area.objects.get(id=id)
    related_objects = []
    for field in instance._meta.related_objects:
        relations = getattr(instance,field.related_name)
        if relations.count() > 0:
            related_objects.append({
                "model": field.related_model.__name__,
                "count": relations.count()
            })

    return JsonResponse({"related_objects":related_objects})

def get_collections(request):
    return JsonResponse(Block.get_collections(), safe=False)


def get_area_types(request):
    area_types = AreaType.objects.all().values('id', 'name').order_by("name")
    data = [{"value": at['id'], "name": at['name']} for at in area_types]
    return JsonResponse(data, safe=False)

def get_area_vaiants(request):
    area = Area.objects.get(id=request.GET.get('id'))
    analyses = VariantCall.objects.filter(
        sample_lib__na_sl_links__nucacid__area_na_links__area=area
    ).select_related('analysis_run').distinct('analysis_run').values(
        'analysis_run_id', 'analysis_run__name'
    )

    response_data = {
        'area': {
            'id': area.id,
            'name': area.name,
            'he_image': area.image.url if area.image else None,
            'block': {
                'name': area.block.name if area.block else '',
                'body_site': area.block.body_site.name if area.block and area.block.body_site else '',
                'diagnosis': area.block.diagnosis if area.block and area.block.diagnosis else ''
            }
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

def get_block_async_by_area(request, id):
    area = Area.objects.get(id=id)
    block = area.block
    block_url = block.get_block_url()
    return JsonResponse({
        'block': {
            'id': block.id,
            'name': block.name,
            'diagnosis': block.diagnosis,
            "aperio_link": f"{block_url}{block.scan_number}" if block.scan_number else "",
        },
        'patient_id': block.patient.pat_id,
    })