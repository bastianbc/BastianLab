from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NucAcids, AREA_NA_LINK
from .forms import *
from areas.models import Area
from method.models import Method
import re
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import *
from core.utils import custom_update
from .serializers import NucacidsSerializer
from django.core import serializers

@permission_required("libprep.view_nucacids",raise_exception=True)
def nucacids(request):
    form = SampleLibCreationOptionsForm()
    filter = FilterForm()
    return render(request, "nucacid_list.html", locals())

@permission_required_for_async("libprep.view_nucacids")
def filter_nucacids(request):
    nucacids = NucAcids().query_by_args(request.user,**request.GET)
    serializer = NucacidsSerializer(nucacids['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = nucacids['draw']
    result['recordsTotal'] = nucacids['total']
    result['recordsFiltered'] = nucacids['count']

    return JsonResponse(result)


@permission_required_for_async("libprep.change_nucacids")
def edit_nucacid_async(request):

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
        nucacid = custom_update(NucAcids,pk=parameters["pk"],parameters=parameters)
    except Exception as e:
        return JsonResponse({"success":False, "message": str(e)})

    return JsonResponse({"success":True})

@permission_required("libprep.add_nucacids",raise_exception=True)
def new_nucacid(request):
    if request.method=="POST":
        form = NucAcidForm(request.POST)
        if form.is_valid():
            nucacid = form.save()
            messages.success(request,"Nuclecic Acid %s created successfully." % nucacid.id)
            return redirect("nucacids")
        else:
            messages.error(request,"Nucleic Acid could not be created.")
    else:
        form = NucAcidForm()

    return render(request,"nucacid.html",locals())

def _generate_unique_name(area, nucleic_acid):
    '''
    Generates a unique name during new record creation.
    Notation: First character of NA_TYPE - Area Name - Increasing number from the same type
    '''
    count = AREA_NA_LINK.objects.filter(area=area, nucacid__name__icontains=nucleic_acid.name).count()
    na_count = count if count>0 else 0
    nucleic_acid.name = "%s-%s-%d" % (area.name, nucleic_acid.na_type[0].upper(), na_count + 1)
    nucleic_acid.save()

@permission_required_for_async("libprep.add_nucacids")
def new_nucacid_async(request):
    selected_ids = json.loads(request.GET.get("selected_ids"))
    options = json.loads(request.GET.get("options"))

    try:
        for id in selected_ids:
            area = Area.objects.get(id=id)
            method = Method.objects.get(id=options["extraction_method"])
            if options["na_type"] == NucAcids.BOTH:
                for na_type in [NucAcids.DNA,NucAcids.RNA]:
                    na = NucAcids.objects.create(
                        na_type=na_type,
                        method=method,
                    )
                    _generate_unique_name(area=area, nucleic_acid=na)
                    AREA_NA_LINK.objects.create(
                        area=area,
                        nucacid=na
                    )

            else:
                na = NucAcids.objects.create(
                    na_type=options["na_type"],
                    method=method
                )
                _generate_unique_name(area=area, nucleic_acid=na)
                AREA_NA_LINK.objects.create(
                    area=area,
                    nucacid=na,
                )

    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required("libprep.change_nucacids",raise_exception=True)
def edit_nucacid(request,id):
    nucacid = NucAcids.objects.get(id=id)

    if request.method=="POST":
        form = NucAcidForm(request.POST,instance=nucacid)
        if form.is_valid():
            nucacid = form.save()
            messages.success(request,"Nuclecic Acid %s updated successfully." % nucacid.id)
            return redirect("nucacids")
        else:
            messages.error(request,"Nucleic Acid could not be updated!")
    else:
        form = NucAcidForm(instance=nucacid)

    return render(request,"nucacid.html",locals())

@permission_required("libprep.delete_nucacids",raise_exception=True)
def delete_nucacid(request,id):
    try:
        nucacid = NucAcids.objects.get(id=id)
        nucacid.delete()
        messages.success(request,"Nucleci Acid %s deleted successfully." % nucacid.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Nuclecic Acid %s could not be deleted!" % nucacid.name)
        deleted = False

    return JsonResponse({ "deleted":deleted })

@permission_required("libprep.delete_nucacids",raise_exception=True)
def delete_batch_nucacids(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        NucAcids.objects.filter(id__in=selected_ids).delete()
    except Exception as e:
        print(str(e))
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

def get_na_types(request):
    return JsonResponse([{"label":"---------","value":""}] + [{ "label":c[1], "value":c[0] } for c in NucAcids.NA_TYPES[:-1]], safe=False)

@permission_required_for_async("blocks.delete_blocks")
def check_can_deleted_async(request):
    id = request.GET.get("id")
    instance = NucAcids.objects.get(id=id)
    related_objects = []
    for field in instance._meta.related_objects:
        relations = getattr(instance,field.related_name)
        if relations.count() > 0:
            related_objects.append({
                "model": field.related_model.__name__,
                "count": relations.count()
            })

    return JsonResponse({"related_objects":related_objects})
