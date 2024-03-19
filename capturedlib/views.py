from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required,permission_required
from .serializers import *
from .models import *
from samplelib.models import SampleLib
from bait.models import Bait
from .forms import *
from django.contrib import messages
from core.decorators import permission_required_for_async

@permission_required("capturedlib.view_capturedlib",raise_exception=True)
def capturedlibs(request):
    form = SequencingLibCreationForm()
    return render(request, "capturedlib_list.html", locals())

@permission_required_for_async("capturedlib.view_capturedlib")
def filter_capturedlibs(request):
    capturedlibs = CapturedLib().query_by_args(request.user,**request.GET)
    serializer = CapturedLibSerializer(capturedlibs['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = capturedlibs['draw']
    result['recordsTotal'] = capturedlibs['total']
    result['recordsFiltered'] = capturedlibs['count']

    return JsonResponse(result)

@permission_required_for_async("capturedlib.change_capturedlib")
def edit_capturedlib_async(request):
    import re
    from core.utils import custom_update
    parameters = {}

    try:
        for k,v in request.POST.items():
            if k.startswith('data'):
                r = re.match(r"data\[(\d+)\]\[(\w+)\]", k)
                if r:
                    parameters["pk"] = r.groups()[0]
                    if v == '':
                        v = None
                    parameters[r.groups()[1]] = v
        captured_lib = custom_update(CapturedLib,pk=parameters["pk"],parameters=parameters)

        # captured_lib.set_nm()
    except Exception as e:
        print("%s in %s" % (str(e),__file__))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required("capturedlib.add_capturedlib",raise_exception=True)
def new_capturedlib(request):
    if request.method=="POST":
        form = CapturedLibForm(request.POST, request.FILES)
        if form.is_valid():
            capturedlib = form.save()
            messages.success(request,"Captured Library %s created successfully." % capturedlib.name)
            return redirect("capturedlibs")
        else:
            messages.error(request,"Captured Library could not be created.")
    else:
        form = CapturedLibForm()

    return render(request,"capturedlib.html",locals())

@permission_required_for_async("capturedlib.add_capturedlib")
def new_capturedlib_async(request):

    selected_ids = json.loads(request.GET.get("selected_ids"))
    options = json.loads(request.GET.get("options"))

    try:
        prefixies = CapturedLib.objects.filter(name__startswith=options["prefix"])
        autonumber = 1
        if prefixies.exists():
            max_value = max([int(p.name.split("-")[-1]) for p in prefixies])
            autonumber = max_value + 1

        samplelibs = SampleLib.objects.filter(id__in=selected_ids)

        bait = Bait.objects.get(id=options["bait"])

        captured_lib = CapturedLib.objects.create(
            name="%s-%d" % (options["prefix"],autonumber),
            date=options["date"],
            bait=bait
        )

        for sample_lib in samplelibs:
            SL_CL_LINK.objects.create(
                captured_lib = captured_lib,
                sample_lib = sample_lib,
                volume = 0
            )

    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False, "error":str(e)})

    return JsonResponse({"success":True})

@permission_required("capturedlib.change_capturedlib",raise_exception=True)
def edit_capturedlib(request,id):
    capturedlib = CapturedLib.objects.get(id=id)

    if request.method=="POST":
        form = CapturedLibForm(request.POST,request.FILES,instance=capturedlib)
        if form.is_valid():
            capturedlib = form.save()
            messages.success(request,"Captured Library %s updated successfully." % capturedlib.name)
            return redirect("capturedlibs")
        else:
            messages.error(request,"Captured Library could not be updated!")
    else:
        form = CapturedLibForm(instance=capturedlib)

    return render(request,"capturedlib.html",locals())

@permission_required("capturedlib.delete_capturedlib",raise_exception=True)
def delete_capturedlib(request,id):
    try:
        capturedlib = CapturedLib.objects.get(id=id)
        capturedlib.delete()
        messages.success(request,"Captured Library %s deleted successfully." % capturedlib.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Captured Library could not be deleted!")
        deleted = False

    return JsonResponse({"deleted":deleted })

@permission_required("capturedlib.delete_capturedlib",raise_exception=True)
def delete_batch_capturedlibs(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        CapturedLib.objects.filter(id__in=selected_ids).delete()
    except Exception as e:
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

@permission_required("samplelib.view_samplelib",raise_exception=True)
def get_used_samplelibs(request,id):
    used_samplelibs = SL_CL_LINK.objects.filter(captured_lib__id=id)
    serializer = UsedSampleLibSerializer(used_samplelibs, many=True)
    return JsonResponse(serializer.data, safe=False)

@permission_required_for_async("capturedlib.change_capturedlib")
def update_async(request,id):
    import math
    try:
        values = json.loads(request.GET.get("values"))
        captured_lib = CapturedLib.objects.get(id=id)
        total_volume = 0

        for value in values:

            volume = float(value["volume"])
            amount = float(value["amount"])


            if math.isnan(volume):
                raise Exception("Invalid input!")

            sample_lib = SampleLib.objects.get(id=value["id"])

            link = SL_CL_LINK.objects.get(captured_lib=captured_lib,sample_lib=sample_lib)

            diff = volume - link.volume

            link.volume = volume
            link.save()

            sample_lib.update_volume(diff)

            total_volume += volume

        captured_lib.vol_init = round(total_volume,2)
        captured_lib.save()
    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False, "message":str(e)})

    return JsonResponse({"success":True})

@permission_required_for_async("samplelib.view_samplelib")
def check_idendical_barcode(request):
    from collections import Counter
    selected_ids = json.loads(request.GET.get("selected_ids"))

    barcode_list = []
    clasheds = []
    is_success = True

    links = SL_CL_LINK.objects.filter(captured_lib__in=selected_ids).values_list("sample_lib__barcode__name","captured_lib__name")

    for i in range(len(links)):
        for j in range(i+1,len(links)):
            if links[i][0] == links[j][0]:
                is_success = False
                if not links[i][1] in clasheds:
                    clasheds.append(links[i][1])
                if not links[j][1] in clasheds:
                    clasheds.append(links[j][1])

    return JsonResponse({
        "clasheds":clasheds,
        "success": is_success
    })

@permission_required_for_async("blocks.delete_blocks")
def check_can_deleted_async(request):
    id = request.GET.get("id")
    instance = CapturedLib.objects.get(id=id)
    related_objects = []
    for field in instance._meta.related_objects:
        relations = getattr(instance,field.related_name)
        if relations.count() > 0:
            related_objects.append({
                "model": field.related_model.__name__,
                "count": relations.count()
            })

    return JsonResponse({"related_objects":related_objects})
