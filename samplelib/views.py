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
from core.decorators import *
from pyairtable import Api
import pandas as pd
from pathlib import Path
from barcodeset.models import Barcodeset, Barcode

@permission_required("samplelib.view_samplelib",raise_exception=True)
def samplelibs(request):
    form = CapturedLibCreationOptionsForm()
    filter = FilterForm()
    return render(request, "samplelib_list.html", locals())

@permission_required_for_async("samplelib.view_samplelib")
def filter_samplelibs(request):
    # _cerate_na_from_at()
    # barcodes()
    samplelibs = SampleLib.query_by_args(request.user,**request.GET)
    serializer = SampleLibSerializer(samplelibs['items'], many=True)

    result = dict()
    result['data'] = serializer.data
    result['draw'] = samplelibs['draw']
    result['recordsTotal'] = samplelibs['total']
    result['recordsFiltered'] = samplelibs['count']

    return JsonResponse(result)

@permission_required_for_async("samplelib.change_samplelib")
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

    try:
        custom_update(SampleLib,pk=parameters["pk"],parameters=parameters)
    except Exception as e:
        return JsonResponse({"success":False, "message": str(e)})

    return JsonResponse({"success":True})

@permission_required("samplelib.add_samplelib",raise_exception=True)
def new_samplelib(request):
    if request.method=="POST":
        form = SampleLibForm(request.POST)
        if form.is_valid():
            samplelib = form.save()
            messages.success(request,"Sample Library %s created successfully." % samplelib.name)
            return redirect("samplelibs")
        else:
            messages.error(request,"Sample Library could not be created.")
    else:
        form = SampleLibForm()

    return render(request,"samplelib.html",locals())

@permission_required_for_async("samplelib.add_samplelib")
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
                shear_volume=float(options["shear_volume"]),
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
                        input_vol= round(used_amount / nucacid.conc,2),
                        input_amount= used_amount
                    )

                    created_links.append(link.id)

                    nucacid.update_volume(used_amount)

                    target_amount -= used_amount

                sample_lib.amount_in = total_amount
                sample_lib.save()
            else:
                nucacid = group.pop()

                used_amount = nucacid.amount if nucacid.amount < target_amount else target_amount

                sample_lib.amount_in = used_amount
                sample_lib.save()

                link = NA_SL_LINK.objects.create(
                    nucacid=nucacid,
                    sample_lib=sample_lib,
                    input_vol= round(used_amount / nucacid.conc, 2),
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
            messages.success(request,"Sample Library %s updated successfully." % samplelib.name)
            return redirect("samplelibs")
        else:
            messages.error(request,"Sample Library could not be updated!")
    else:
        form = SampleLibForm(instance=samplelib)

    return render(request,"samplelib.html",locals())

@permission_required("samplelib.delete_samplelib",raise_exception=True)
def delete_samplelib(request,id):
    try:
        samplelib = SampleLib.objects.get(id=id)
        samplelib.delete()
        messages.success(request,"Sample Library %s deleted successfully." % samplelib.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Sample Library could not be deleted!")
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

@permission_required_for_async("samplelib.change_samplelib")
def update_sl_na_link_async(request):
    try:
        values = json.loads(request.GET.get("values"))

        for value in values:
            link = NA_SL_LINK.objects.get(id=value["id"])

            volume = float(value["volume"])
            amount = float(value["amount"])
            te = float(value["te"])

            diff = amount - link.input_amount

            link.input_vol = volume
            link.input_amount = amount
            link.save()

            sample_lib = link.sample_lib
            sample_lib.amount_in = amount
            sample_lib.shear_volume = te + volume
            sample_lib.save()

            link.nucacid.update_volume(diff)
    except Exception as e:
        print(str(e))
        return JsonResponse({ "success":False })

    return JsonResponse({ "success":True })

def print_as_csv(request):
    import csv
    from django.http import HttpResponse

    class Report(object):
        sample_lib = ""
        nucacid = ""
        input_vol = 0.0
        input_amount = 0.0
        te = 0.0

    selected_ids = json.loads(request.GET.get("selected_ids"))

    result = []

    for sl_link in NA_SL_LINK.objects.filter(id__in=selected_ids):
        report = Report()
        report.sample_lib = sl_link.sample_lib.name
        report.nucacid = sl_link.nucacid.name
        report.input_vol = sl_link.input_vol
        report.input_amount = sl_link.input_amount
        report.te = sl_link.sample_lib.shear_volume - sl_link.input_vol
        result.append(report)

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="used_nucacids.csv"'},
    )

    field_names = ["sample_lib","nucacid","input_vol","input_amount","te"]
    writer = csv.writer(response)
    writer.writerow(field_names)
    for item in result:
        writer.writerow([getattr(item, field) for field in field_names])

    return response

@permission_required_for_async("blocks.delete_blocks")
def check_can_deleted_async(request):
    id = request.GET.get("id")
    instance = SampleLib.objects.get(id=id)
    related_objects = []
    for field in instance._meta.related_objects:
        relations = getattr(instance,field.related_name)
        if relations.count() > 0:
            related_objects.append({
                "model": field.related_model.__name__,
                "count": relations.count()
            })

    return JsonResponse({"related_objects":related_objects})


def create_na_sl_link(sl, value, lp_dna, qPCR):
    try:
        vol = round(lp_dna / qPCR, 2)
    except Exception as e:
        vol = 0

    for na in value.split(","):
        na = NucAcids.objects.get(name=na)
        na_sl_link = NA_SL_LINK.objects.filter(
            nucacid=na,
            sample_lib=sl
        ).update(input_vol=vol)
        print("na_sl_link updated")


def sl_get_or_create_at(row):
    try:
        if pd.isnull(row["New Barcode"]) and pd.isnull(row["Old Barcode"]):
            return
        sl = SampleLib.objects.get(name=row["SL_ID"])
        barcode = row["New Barcode"] or row["Old Barcode"]
        print(row["SL_ID"], row["New Barcode"] , row["Old Barcode"], barcode)
        try:
            sl.barcode = Barcode.objects.get(name=barcode)
            sl.save()
            print("saved")
        except Exception as e:
            print(e)
        # sl.qubit = row["Post-lib Qubit (ng/ul)"]
        # # sl.shear_volume = row["Post-lib qPCR (ng/ul)"] #TODO need to return this from NA table
        # sl.qpcr_conc = row["Post-lib qPCR (ng/ul)"]
        # sl.pcr_cycles = row["Post-hyb PCR cycles"]
        # sl.amount_final = row["Total LP DNA for capture (ng)"]
        # sl.vol_init = row["Total LP DNA for capture (ng)"]
        # sl.notes = row["Notes"]
        # sl.save()
        # if not pd.isnull(row["NA_ID"]):
        #     create_na_sl_link(sl, row["NA_ID"], row["LP DNA (ng)"], row["Post-lib qPCR (ng/ul)"])
        # print("saved")
    except Exception as e:
        print(e)


def _cerate_na_from_at():
    file = Path(Path(__file__).parent.parent / "uploads" / "Sample Library with grid view, analysis view and more-Grid view-6.csv")
    df = pd.read_csv(file)
    df[~pd.isnull(df["SL_ID"])].apply(lambda row: sl_get_or_create_at(row), axis=1)



def sl_get_or_create_consolidated_2(row):
    try:
        print(row["Sample"])
        SampleLib.objects.create(name=row["Sample"])
        print("created")
    except Exception as e:
        print(e)

def sl_get_or_create_consolidated_3(row):
    try:
        if pd.isnull(row["NA_id"]):
            return
        print(row["Sample"], row["NA_id"])
        NA_SL_LINK.objects.get(nucacid=row["Sample"],sample_lib=row["NA_id"])
        print("pass")
    except Exception as e:
        try:
            sl = SampleLib.objects.get(name=row["Sample"])
            na = NucAcids.objects.get(name=row["NA_id"])
            NA_SL_LINK.objects.create(nucacid=na, sample_lib=sl)
            print("created")
        except Exception as e:
            print(e)

def _cerate_na_from_consolidated_data_2():
    file = Path(Path(__file__).parent.parent / "uploads" / "Consolidated_data_final.csv")
    df = pd.read_csv(file)
    df[~pd.isnull(df["Sample"])].apply(lambda row: sl_get_or_create_consolidated_3(row), axis=1)

def barcode_get(row):
    print(row["Barcode_ID"])
    try:
        Barcode.objects.get(name=row["Barcode_ID"])
    except:
        Barcode.objects.create(name=row["Barcode_ID"],
                               barcode_set=Barcodeset.objects.get(name="Old Barcodes"),
                               i5=row["Index-i5"],
                               i7=row["Index-i7"]
                               )
        print("created")

def barcodes():
    file = Path(Path(__file__).parent.parent / "uploads" / "Old Barcodes-Grid view-2.csv")
    df = pd.read_csv(file)
    df.apply(lambda row: barcode_get(row), axis=1)
    # df[~pd.isnull(df["Old Barcode"])].apply(lambda row: barcode_get(row), axis=1)
