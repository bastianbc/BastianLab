from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required,permission_required
from .serializers import *
from .models import *
from .forms import *
from django.contrib import messages
from capturedlib.models import *

@permission_required("sequencinglib.view_sequencinglib",raise_exception=True)
def sequencinglibs(request):
    return render(request, "sequencinglib_list.html", locals())

@login_required
def filter_sequencinglibs(request):
    sequencinglibs = SequencingLib().query_by_args(request.user,**request.GET)
    serializer = SequencingLibSerializer(sequencinglibs['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = sequencinglibs['draw']
    result['recordsTotal'] = sequencinglibs['total']
    result['recordsFiltered'] = sequencinglibs['count']

    return JsonResponse(result)

@permission_required("sequencinglib.change_sequencinglib",raise_exception=True)
def edit_sequencinglib_async(request):
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

    sequencing_lib = custom_update(SequencingLib,pk=parameters["pk"],parameters=parameters)

    sequencing_lib.set_nm()

    return JsonResponse({"result":True})

@permission_required("sequencinglib.add_sequencinglib",raise_exception=True)
def new_sequencinglib(request):
    if request.method=="POST":
        form = SequencingLibForm(request.POST, request.FILES)
        if form.is_valid():
            sequencinglib = form.save()
            messages.success(request,"Captured Library %s was created successfully." % sequencinglib.name)
            return redirect("sequencinglibs")
        else:
            messages.error(request,"Captured Library wasn't created.")
    else:
        form = SequencingLibForm()

    return render(request,"sequencinglib.html",locals())

@permission_required("sequencinglib.add_sequencinglib",raise_exception=True)
def new_sequencinglib_async(request):

    selected_ids = json.loads(request.GET.get("selected_ids"))
    options = json.loads(request.GET.get("options"))

    try:
        prefixies = SequencingLib.objects.filter(name__startswith=options["prefix"])
        autonumber = 1
        if prefixies.exists():
            max_value = max([int(p.name.split("-")[-1]) for p in prefixies])
            autonumber = max_value + 1

        capturedlibs = CapturedLib.objects.filter(id__in=selected_ids)

        sequencing_lib = SequencingLib.objects.create(
            name="%s-%d" % (options["prefix"],autonumber),
            date=options["date"],
            buffer=options["buffer"]
        )

        for captured_lib in capturedlibs:
            # target_mol = conc * vol
            # CLcount = the number CLs selected
            # Calculate CL_Seq_L_link.volume for each CL using (target_mol/CLcount)/CL.nM

            CL_SEQL_LINK.objects.create(
                sequencing_lib = sequencing_lib,
                captured_lib = captured_lib,
                volume = ((float(options["conc"]) * float(options["vol_init"])) / len(selected_ids))/captured_lib.nm
            )

    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required("sequencinglib.add_sequencinglib",raise_exception=True)
def recreate_sequencinglib_async(request):

    selected_ids = json.loads(request.GET.get("selected_ids"))
    options = json.loads(request.GET.get("options"))

    try:
        sequencing_lib = SequencingLib.objects.get(id=options["id"])

        capturedlibs = CapturedLib.objects.filter(id__in=selected_ids)

        CL_SEQL_LINK.objects.filter(sequencing_lib=sequencing_lib).delete()

        for captured_lib in capturedlibs:
            # target_mol = conc * vol
            # CLcount = the number CLs selected
            # Calculate CL_Seq_L_link.volume for each CL using (target_mol/CLcount)/CL.nM

            CL_SEQL_LINK.objects.create(
                sequencing_lib = sequencing_lib,
                captured_lib = captured_lib,
                volume = ((float(options["conc"]) * float(options["vol_init"])) / len(selected_ids))/captured_lib.nm
            )

    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required("sequencinglib.change_sequencinglib",raise_exception=True)
def edit_sequencinglib(request,id):
    sequencinglib = SequencingLib.objects.get(id=id)

    if request.method=="POST":
        form = SequencingLibForm(request.POST,request.FILES,instance=sequencinglib)
        if form.is_valid():
            sequencinglib = form.save()
            messages.success(request,"Captured Library %s was updated successfully." % sequencinglib.name)
            return redirect("sequencinglibs")
        else:
            messages.error(request,"Captured Library wasn't updated!")
    else:
        form = SequencingLibForm(instance=sequencinglib)

    return render(request,"sequencinglib.html",locals())

@permission_required("sequencinglib.delete_sequencinglib",raise_exception=True)
def delete_sequencinglib(request,id):
    try:
        sequencinglib = SequencingLib.objects.get(id=id)
        sequencinglib.delete()
        messages.success(request,"Captured Library %s was deleted successfully." % sequencinglib.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Captured Library wasn't deleted!")
        deleted = False

    return JsonResponse({"deleted":deleted })

@permission_required("sequencinglib.delete_sequencinglib",raise_exception=True)
def delete_batch_sequencinglibs(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        SequencingLib.objects.filter(id__in=selected_ids).delete()
    except Exception as e:
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

@permission_required("sequencinglib.view_sequencinglib",raise_exception=True)
def get_used_capturedlibs(request,id):
    used_capturedlibs = CL_SEQL_LINK.objects.filter(sequencing_lib__id=id)
    serializer = UsedCapturedLibSerializer(used_capturedlibs, many=True)
    return JsonResponse(serializer.data, safe=False)

@permission_required("sequencinglib.change_sequencinglib",raise_exception=True)
def update_async(request,id):
    try:
        values = json.loads(request.GET.get("values"))
        sequencing_lib = SequencingLib.objects.get(id=id)
        for value in values:
            volume = float(value["volume"])

            sample_lib = SampleLib.objects.get(id=value["id"])

            link = SL_CL_LINK.objects.get(sequencing_lib=sequencing_lib,sample_lib=sample_lib)
            link.volume = volume
            link.save()

            sample_lib.update_volume(volume)
    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})
