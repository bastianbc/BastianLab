from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NucAcids
from .forms import *
from areas.models import Areas
from method.models import Method
import re
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import *
from core.utils import custom_update
from .serializers import NucacidsSerializer
from pyairtable import Api
import pandas as pd
from pathlib import Path


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
            messages.success(request,"Nuclecic Acid %s was created successfully." % nucacid.nu_id)
            return redirect("nucacids")
        else:
            messages.error(request,"Nucleic Acid wasn't created.")
    else:
        form = NucAcidForm()

    return render(request,"nucacid.html",locals())

@permission_required_for_async("libprep.add_nucacids")
def new_nucacid_async(request):
    selected_ids = json.loads(request.GET.get("selected_ids"))
    options = json.loads(request.GET.get("options"))

    try:
        for id in selected_ids:
            area = Areas.objects.get(ar_id=id)
            method = Method.objects.get(id=options["extraction_method"])

            if options["na_type"] == NucAcids.BOTH:
                for na_type in [NucAcids.DNA,NucAcids.RNA]:
                    NucAcids.objects.create(
                        area=area,
                        na_type=na_type,
                        method=method
                    )
            else:
                NucAcids.objects.create(
                    area=area,
                    na_type=options["na_type"],
                    method=method
                )

    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required("libprep.change_nucacids",raise_exception=True)
def edit_nucacid(request,id):
    nucacid = NucAcids.objects.get(nu_id=id)

    if request.method=="POST":
        form = NucAcidForm(request.POST,instance=nucacid)
        if form.is_valid():
            nucacid = form.save()
            messages.success(request,"Nuclecic Acid %s was updated successfully." % nucacid.nu_id)
            return redirect("nucacids")
        else:
            messages.error(request,"Nucleic Acid wasn't updated!")
    else:
        form = NucAcidForm(instance=nucacid)

    return render(request,"nucacid.html",locals())

@permission_required("libprep.delete_nucacids",raise_exception=True)
def delete_nucacid(request,id):
    try:
        nucacid = NucAcids.objects.get(nu_id=id)
        nucacid.delete()
        messages.success(request,"Nucleci Acid %s was deleted successfully." % nucacid.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Nuclecic Acid %s wasn't deleted!" % nucacid.name)
        deleted = False

    return JsonResponse({ "deleted":deleted })

@permission_required("libprep.delete_nucacids",raise_exception=True)
def delete_batch_nucacids(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        NucAcids.objects.filter(nu_id__in=selected_ids).delete()
    except Exception as e:
        print(str(e))
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

def get_na_types(request):
    return JsonResponse([{"label":"---------","value":""}] + [{ "label":c[1], "value":c[0] } for c in NucAcids.NA_TYPES[:-1]], safe=False)

@permission_required_for_async("blocks.delete_blocks")
def check_can_deleted_async(request):
    id = request.GET.get("id")
    instance = NucAcids.objects.get(nu_id=id)
    related_objects = []
    for field in instance._meta.related_objects:
        relations = getattr(instance,field.related_name)
        if relations.count() > 0:
            related_objects.append({
                "model": field.related_model.__name__,
                "count": relations.count()
            })

    return JsonResponse({"related_objects":related_objects})


def get_na_type(value):
    for x in NucAcids.NA_TYPES:
        if value.lower() == x[1].lower():
            return x[0]
    return None


def get_or_create_method(value):
    if value:
        obj, created = Method.objects.get_or_create(
            name=value
        )
        return obj
    return None

def get_or_create_na_from_file(row):
    try:
        print(row["NA_ID"], row["Area ID"])
        if pd.isnull(row["Area ID"]):
            a = Areas.objects.get(name="UndefinedArea")
        else:
            try:
                a = Areas.objects.get(name=row["Area ID"])
            except:
                a = Areas.objects.get(name="UndefinedArea")
                print(f" {row['Area ID']} Areas matching query does not exist")
        na = NucAcids.objects.get(name=row["NA_ID"])
        na.area = a
        na.conc = row["Qubit Concentration (ng/ul)"]
        na.vol_init = row["Volumn (ul)"]
        na.na_type = get_na_type(row["NA_TYPE"]) if not pd.isnull(row["NA_TYPE"]) else ""
        na.method = get_or_create_method(row["Method"])
        na.save()
        print("saved")
    except Exception as e:
        print("error"*5,e)

def get_o(row):
    area_id = row["Area ID"].split(",")[0].strip()
    print(row["Area ID"])
    # try:
    #     try:
    #         a = Areas.objects.get(name=area_id)
    #     except:
    #         a = Areas.objects.get(name="UndefinedArea")
    #         print(f" {area_id} Areas matching query does not exist")
    #
    #     na = NucAcids.objects.get(name=row["NA_ID"])
    #     na.area = a
    #     print("saved")
    # except Exception as e:
    #     print("error"*5,e)

def _create_areas_from_file():
    file = Path(Path(__file__).parent.parent / "uploads" / "Nucleic Acids-Grid view-4.csv")
    df = pd.read_csv(file)
    # print(df[df["Block_ID"]])
    # df[~df["NA_ID"].isnull()].apply(lambda row: get_or_create_na_from_file(row), axis=1)
    df[df["Area ID"].str.contains(",") & df["Area ID"].notna()].apply(lambda row: get_o(row), axis=1)


def _na_get_or_create_consolidated(row):
    try:
        print(row["NA_id"], row["Area_id"])
        na = NucAcids.objects.get(name=row["NA_id"])
        na.area = Areas.objects.get(name=row["Area_id"])
        na.save()
        print("saved")
    except Exception as e:
        try:
            NucAcids.objects.create(
                name=row["NA_id"],
                area=Areas.objects.get(name=row["Area_id"])
            )
            print("created"*3)
        except Exception as ed:
            print("not created", ed)

def _cerate_na_from_consolidated_data():
    file = Path(Path(__file__).parent.parent / "uploads" / "Consolidated_data_final.csv")
    df = pd.read_csv(file)
    df[~df["NA_id"].isnull()].apply(lambda row: _na_get_or_create_consolidated(row), axis=1)



