from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SampleLib
from .forms import *
from .models import *
from areas.models import Areas
from method.models import Method
from libprep.models import NucAcids
import re
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required,permission_required

@permission_required("samplelib.view_samplelib",raise_exception=True)
def samplelibs(request):
    return render(request, "samplelib_list.html", locals())

@login_required
def filter_samplelibs(request):
    from .serializers import SampleLibSerializer

    samplelibs = SampleLib().query_by_args(request.user,**request.GET)
    serializer = SampleLibSerializer(samplelibs['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = samplelibs['draw']
    result['recordsTotal'] = samplelibs['total']
    result['recordsFiltered'] = samplelibs['count']

    return JsonResponse(result)

@permission_required("samplelib.change_samplelib",raise_exception=True)
def edit_samplelib_async(request):
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

@permission_required("samplelib.add_samplelib",raise_exception=True)
def new_samplelib(request):
    if request.method=="POST":
        form = SampleLibForm(request.POST)
        if form.is_valid():
            samplelib = form.save()
            messages.success(request,"Sample Library %s was created successfully." % samplelib.name)
            return redirect("samplelibs")
        else:
            messages.error(request,"Sample Library wasn't created.")
    else:
        form = SampleLibForm()

    return render(request,"samplelib.html",locals())

@permission_required("samplelib.add_samplelib",raise_exception=True)
def new_samplelib_async(request):
    from .utils import get_smallest_amount_nucleic_acid

    selected_ids = json.loads(request.GET.get("selected_ids"))
    options = json.loads(request.GET.get("options"))

    try:
        area = {}

        barcode_id = int(options["barcode_start_with"])

        nucacids = NucAcids.objects.filter(nu_id__in=selected_ids).order_by("vol_remain")

        prefixies = SampleLib.objects.filter(name__startswith=options["prefix"])
        autonumber = 1
        if prefixies.exists():
            max_value = max([int(p.name.split("-")[-1]) for p in prefixies])
            autonumber = max_value + 1

        for nucacid in nucacids:
            sample_lib = {}

            if not area == nucacid.area:
                area = nucacid.area

                barcode = Barcode.objects.get(id=barcode_id)

                sample_lib = SampleLib.objects.create(
                    name="%s-%d" % (options["prefix"],autonumber),
                    barcode=barcode,
                    method=Method.objects.all().first(),
                )

            NA_SL_LINK.objects.create(
                nucacid=nucacid,
                sample_lib=sample_lib,
                input_vol=nucacid.vol_remain,
                input_amount=float(options["target_amount"]) - nucacid.vol_remain
            )

            nucacid.set_zero_volume()
            # nucacid.update_volume(float(options["target_amount"]))

            barcode_id = barcode_id + 1 if barcode_id < 192 else 1 #The barcode table contains numeric barcodes with barcode_id=1- 192

    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required("samplelib.change_samplelib",raise_exception=True)
def edit_samplelib(request,id):
    samplelib = SampleLib.objects.get(nu_id=id)

    if request.method=="POST":
        form = SampleLibForm(request.POST,instance=samplelib)
        if form.is_valid():
            samplelib = form.save()
            messages.success(request,"Sample Library %s was updated successfully." % samplelib.name)
            return redirect("samplelibs")
        else:
            messages.error(request,"Sample Library wasn't updated!")
    else:
        form = SampleLibForm(instance=samplelib)

    return render(request,"samplelib.html",locals())

@permission_required("samplelib.delete_samplelib",raise_exception=True)
def delete_samplelib(request,id):
    try:
        samplelib = SampleLib.objects.get(id=id)
        samplelib.delete()
        messages.success(request,"Sample Library %s was deleted successfully." % samplelib.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Sample Library wasn't deleted!")
        deleted = False

    return JsonResponse({"deleted":deleted })
