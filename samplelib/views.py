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
from .serializers import *
from django.db.models import Q

@permission_required("samplelib.view_samplelib",raise_exception=True)
def samplelibs(request):
    form = CapturedLibCreationOptionsForm()
    return render(request, "samplelib_list.html", locals())

@login_required
def filter_samplelibs(request):
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
    from itertools import groupby

    selected_ids = json.loads(request.GET.get("selected_ids"))
    options = json.loads(request.GET.get("options"))
    created_links = []

    try:

        barcode_id = int(options["barcode_start_with"])

        target_amount = used_amount = float(options["target_amount"])

        nucacids = NucAcids.objects.filter(Q(nu_id__in=selected_ids) & Q(vol_remain__gt=0))

        grouped_nucacids = [list(result) for key, result in groupby(sorted(nucacids,key=lambda na: na.area.ar_id), key=lambda na: na.area.ar_id)]

        prefixies = SampleLib.objects.filter(name__startswith=options["prefix"])
        autonumber = 1
        if prefixies.exists():
            max_value = max([int(p.name.split("-")[-1]) for p in prefixies])
            autonumber = max_value + 1

        for group in grouped_nucacids:

            sample_lib = SampleLib.objects.create(
                name="%s-%d" % (options["prefix"],autonumber),
                barcode=Barcode.objects.get(id=barcode_id),
                method=Method.objects.all().first(),
            )

            if len(group) > 1:

                total_amount = 0

                sorted_group = sorted(group, key=lambda na: na.amount, reverse=True)

                while target_amount > 0 and len(sorted_group) > 0:

                    nucacid = sorted_group.pop()

                    used_amount = nucacid.amount if nucacid.amount < target_amount else target_amount
                    total_amount += used_amount

                    link = NA_SL_LINK.objects.create(
                        nucacid=nucacid,
                        sample_lib=sample_lib,
                        input_vol= used_amount / nucacid.conc,
                        input_amount= used_amount
                    )

                    created_links.append(link.id)

                    nucacid.update_volume(used_amount)

                    target_amount -= used_amount

                sample_lib.input_amount = total_amount
                sample_lib.save()
            else:
                nucacid = group.pop()

                used_amount = nucacid.amount if nucacid.amount < target_amount else target_amount

                sample_lib.input_amount = used_amount
                sample_lib.save()

                link = NA_SL_LINK.objects.create(
                    nucacid=nucacid,
                    sample_lib=sample_lib,
                    input_vol= used_amount / nucacid.conc,
                    input_amount= used_amount
                )

                created_links.append(link.id)
                nucacid.update_volume(used_amount)

            barcode_id = (barcode_id % 192) + 1 #The barcode table contains numeric barcodes with barcode_id=1- 192
            autonumber += 1

        saved_links = NA_SL_LINK.objects.filter(id__in=created_links).order_by("nucacid__area")
        serializer = SavedNuacidsSerializer(saved_links, many=True)

    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False, "data":None})

    return JsonResponse({"success":True, "data":serializer.data})

@permission_required("samplelib.change_samplelib",raise_exception=True)
def edit_samplelib(request,id):
    samplelib = SampleLib.objects.get(id=id)

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

@permission_required("samplelib.delete_samplelib",raise_exception=True)
def delete_batch_samplelibs(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        SampleLib.objects.filter(id__in=selected_ids).delete()
    except Exception as e:
        print(str(e))
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

@permission_required("samplelib.view_samplelib",raise_exception=True)
def get_used_nucacids(request,id):
    used_nucacids = NA_SL_LINK.objects.filter(sample_lib__id=id)
    serializer = UsedNuacidsSerializer(used_nucacids, many=True)
    return JsonResponse(serializer.data, safe=False)

@permission_required("samplelib.change_samplelib",raise_exception=True)
def update_sl_na_link_async(request):
    try:
        values = json.loads(request.GET.get("values"))

        for value in values:
            link = NA_SL_LINK.objects.get(id=value["id"])

            volume = float(value["volume"])
            amount = float(value["amount"])

            diff = amount - link.input_amount

            link.input_vol = volume
            link.input_amount = amount
            link.save()

            sample_lib = link.sample_lib
            sample_lib.amount_in = amount
            sample_lib.save()

            link.nucacid.update_volume(diff)
    except Exception as e:
        print(str(e))
        return JsonResponse({ "success":False })

    return JsonResponse({ "success":True })

def print_as_csv(request,id):
    import csv
    from django.http import HttpResponse

    class Report(object):
        sample_lib = ""
        nucacid = ""
        input_vol = 0.0
        input_amount = 0.0

    result = []

    for sl_link in NA_SL_LINK.objects.filter(sample_lib__id=id):
        report = Report()
        report.sample_lib = sl_link.sample_lib.name
        report.nucacid = sl_link.nucacid.name
        report.input_vol = sl_link.input_vol
        report.input_amount = sl_link.input_amount
        result.append(report)

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="used_nucacids.csv"'},
    )

    field_names = ["sample_lib","nucacid","input_vol","input_amount"]
    writer = csv.writer(response)
    writer.writerow(field_names)
    for item in result:
        writer.writerow([getattr(item, field) for field in field_names])

    return response
