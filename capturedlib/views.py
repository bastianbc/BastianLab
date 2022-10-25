from django.shortcuts import render
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required,permission_required
from .serializers import *
from .models import *
from samplelib.models import SampleLib, Barcode

@permission_required("capturedlib.view_capturedlib",raise_exception=True)
def capturedlibs(request):
    return render(request, "capturedlib_list.html", locals())

@login_required
def filter_capturedlibs(request):
    capturedlibs = CapturedLib().query_by_args(request.user,**request.GET)
    serializer = CapturedLibSerializer(capturedlibs['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = capturedlibs['draw']
    result['recordsTotal'] = capturedlibs['total']
    result['recordsFiltered'] = capturedlibs['count']

    return JsonResponse(result)

@permission_required("capturedlib.change_capturedlib",raise_exception=True)
def edit_capturedlib_async(request):
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

    custom_update(SampleLib,pk=parameters["pk"],parameters=parameters)

    return JsonResponse({"result":True})

@permission_required("capturedlib.add_capturedlib",raise_exception=True)
def new_capturedlib(request):
    if request.method=="POST":
        form = SampleLibForm(request.POST)
        if form.is_valid():
            capturedlib = form.save()
            messages.success(request,"Sample Library %s was created successfully." % capturedlib.name)
            return redirect("capturedlibs")
        else:
            messages.error(request,"Sample Library wasn't created.")
    else:
        form = SampleLibForm()

    return render(request,"capturedlib.html",locals())

@permission_required("capturedlib.add_capturedlib",raise_exception=True)
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

        barcode = Barcode.objects.first()

        captured_lib = CapturedLib.objects.create(
            name="%s-%d" % (options["prefix"],autonumber),
            barcode=barcode,
            date=options["date"],
            bait=options["bait"]
        )

        for sample_lib in samplelibs:
            SL_CL_LINK.objects.create(
                captured_lib = captured_lib,
                sample_lib = sample_lib,
                volume = 0
            )

    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required("capturedlib.change_capturedlib",raise_exception=True)
def edit_capturedlib(request,id):
    capturedlib = SampleLib.objects.get(id=id)

    if request.method=="POST":
        form = SampleLibForm(request.POST,instance=capturedlib)
        if form.is_valid():
            capturedlib = form.save()
            messages.success(request,"Sample Library %s was updated successfully." % capturedlib.name)
            return redirect("capturedlibs")
        else:
            messages.error(request,"Sample Library wasn't updated!")
    else:
        form = SampleLibForm(instance=capturedlib)

    return render(request,"capturedlib.html",locals())

@permission_required("capturedlib.delete_capturedlib",raise_exception=True)
def delete_capturedlib(request,id):
    try:
        capturedlib = SampleLib.objects.get(id=id)
        capturedlib.delete()
        messages.success(request,"Sample Library %s was deleted successfully." % capturedlib.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Sample Library wasn't deleted!")
        deleted = False

    return JsonResponse({"deleted":deleted })

@permission_required("capturedlib.delete_capturedlib",raise_exception=True)
def delete_batch_capturedlibs(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        SampleLib.objects.filter(id__in=selected_ids).delete()
    except Exception as e:
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

@permission_required("samplelib.view_samplelib",raise_exception=True)
def get_used_samplelibs(request,id):
    used_samplelibs = SL_CL_LINK.objects.filter(captured_lib__id=id)
    serializer = UsedSampleLibSerializer(used_samplelibs, many=True)
    return JsonResponse(serializer.data, safe=False)

@permission_required("capturedlib.change_capturedlib",raise_exception=True)
def update_async(request,id):
    try:
        values = json.loads(request.GET.get("values"))

        for value in values:
            link = SL_CL_LINK.objects.get(captured_lib__id=id,sample_lib__id=value["id"])
            link.volume = float(value["volume"])
            link.save()
    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})
