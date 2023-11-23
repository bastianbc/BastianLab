from django.shortcuts import render, redirect
from .models import Blocks
from .forms import *
from django.http import JsonResponse
import json
from django.contrib import messages
from lab.models import Patients
from projects.models import Projects
from .serializers import BlocksSerializer
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async
import pandas as pd
from pathlib import Path
from method.models import Method


@permission_required_for_async("blocks.view_blocks")
def filter_blocks(request):
    from .serializers import BlocksSerializer
    # _create_blocks_from_file()
    blocks = Blocks.query_by_args(request.user,**request.GET)
    serializer = BlocksSerializer(blocks['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = blocks['draw']
    result['recordsTotal'] = blocks['total']
    result['recordsFiltered'] = blocks['count']
    print(result['data'])
    return JsonResponse(result)

@permission_required("blocks.view_blocks",raise_exception=True)
def blocks(request):
    id = request.GET.get("id")
    model = request.GET.get("model")

    form = AreaCreationForm()

    if model=="project" and id:
        project = Projects.objects.get(pr_id=id)
    elif model=="patient" and id:
        patient = Patients.objects.get(pat_id=id)

    return render(request,"block_list.html",locals())

@permission_required("blocks.add_blocks",raise_exception=True)
def new_block(request):
    if request.method=="POST":
        form = BlockForm(request.POST)
        if form.is_valid():
            block = form.save()
            messages.success(request,"Block %s created successfully." % block.bl_id)
            return redirect("blocks")
        else:
            messages.error(request,"Block not created.")
    else:
        form = BlockForm()

    return render(request,"block.html",locals())

@permission_required_for_async("blocks.add_blocks")
def add_block_to_patient_async(request):
    selected_ids = json.loads(request.GET.get("selected_ids"))

    try:
        for id in selected_ids:
            patient = Patients.objects.get(pat_id=id)
            Blocks.objects.create(patient=patient)
    except Exception as e:
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required_for_async("blocks.add_blocks")
def add_block_to_project_async(request):
    selected_ids = json.loads(request.GET.get("selected_ids"))
    project_id = request.GET.get("project_id")

    try:
        project = Projects.objects.get(pr_id=project_id)
        for id in selected_ids:
            block = Blocks.objects.get(bl_id=id)
            block.project = project
            block.save()
    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required_for_async("blocks.change_blocks")
def remove_block_from_project_async(request):
    selected_ids = json.loads(request.GET.get("selected_ids"))
    project_id = request.GET.get("project_id")

    try:
        project = Projects.objects.get(pr_id=project_id)
        for id in selected_ids:
            block = Blocks.objects.get(bl_id=id)
            block.project = None
            block.save()
    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required("blocks.change_blocks",raise_exception=True)
def edit_block(request,id):
    block = Blocks.objects.get(bl_id=id)

    if request.method=="POST":
        form = BlockForm(request.POST,instance=block)
        if form.is_valid():
            block = form.save()
            messages.success(request,"The block updated successfully.")
            return redirect("blocks")
        else:
            messages.error(request,"The block not updated!")
    else:
        form = BlockForm(instance=block)

    return render(request,"block.html",locals())

@permission_required_for_async("blocks.change_blocks")
def edit_block_async(request):
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
        custom_update(Blocks,pk=parameters["pk"],parameters=parameters)
    except Exception as e:
        return JsonResponse({"success":False, "message": str(e)})

    return JsonResponse({"success":True})

@permission_required_for_async("blocks.delete_blocks")
def delete_block(request,id):
    try:
        block = Blocks.objects.get(bl_id=id)
        block.delete()
        messages.success(request,"Block %s deleted successfully." % block.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Block %s not deleted!" % block.pat_id)
        deleted = False

    return JsonResponse({ "deleted":deleted })

@permission_required("blocks.delete_blocks",raise_exception=True)
def delete_batch_blocks(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        Blocks.objects.filter(bl_id__in=selected_ids).delete()
    except Exception as e:
        print(str(e))
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

@permission_required_for_async("blocks.delete_blocks")
def check_can_deleted_async(request):
    id = request.GET.get("id")
    instance = Blocks.objects.get(bl_id=id)
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
    return JsonResponse(Blocks.get_collections(), safe=False)

def export_csv_all_data(request):
    import csv
    from django.http import HttpResponse

    result = []

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="blocks.csv"'},
    )

    field_names = [f.name for f in Blocks._meta.fields]
    writer = csv.writer(response)
    writer.writerow(field_names)
    for patient in Blocks.objects.all():
        writer.writerow([getattr(patient, field) for field in field_names])

    return response


def edit_block_url(request):
    instance = BlockUrl.objects.first()
    if request.method=="POST":
        form = BlockUrlForm(request.POST,instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request,"Block URL was updated successfully")
            # return redirect('/blocks/edit_block_url')
        else:
            messages.error(request,"Block URL wasn't updated!")
    else:
        form = BlockUrlForm(instance=instance)
    return render(request,"block_url.html",locals())


def _assign_projects_to_blocks():
    from pyairtable import Api
    api = Api('keyEDswuVpUGOz8Tp')
    t = api.table("appA7qA5hhuLgiAwt", "tblv5WQXW7cNCbt0o")
    for i in t.all():
        for s in i.get("fields").get("Assigned project", []):
            try:
                p = Projects.objects.get(name=s.strip())
                b = Blocks.objects.get(name=i.get("fields").get("Block_ID", ""))
            except Exception as e:
                print(i.get("fields").get("Block_ID", ""))
                print(e)
            b.project = p
            b.save()
            print("saved")


def _assign_patients_to_blocks():
    from pyairtable import Api
    api = Api('keyEDswuVpUGOz8Tp')
    pat_table = api.table("appA7qA5hhuLgiAwt", "tblxWxK1fH2VMbI4Q")
    block_table = api.table("appA7qA5hhuLgiAwt", "tblv5WQXW7cNCbt0o")

    for pat in pat_table.all():
        for block in pat.get("fields").get("Blocks _ID", []):

            try:
                bb = block_table.get(block).get("fields").get("Block_ID", "")

                p = Patients.objects.get(pat_id=pat.get("fields").get("Pat_ID", []))
                b = Blocks.objects.get(name=bb)
                b.patient = p
                b.save()

            except Exception as e:
                print(pat.get("fields").get("Block_ID", ""))
                print(e)

def get_pat_id(pk):
    from pyairtable import Api
    api = Api('keyEDswuVpUGOz8Tp')
    pat_table = api.table("appA7qA5hhuLgiAwt", "tblxWxK1fH2VMbI4Q")
    try:
        res = pat_table.get(pk[0])
        p = Patients.objects.get(pat_id=res.get("fields").get("Pat_ID"))
        return p
    except Exception as e:
        print(e)


def get_project_id(pk):
    from pyairtable import Api
    api = Api('keyEDswuVpUGOz8Tp')
    pro_table = api.table("appA7qA5hhuLgiAwt", "tblT4u7Cgb4fUgaiI")
    try:
        res = pro_table.get(pk[0])
        p = Projects.objects.get(name=res.get("fields").get("Assigned Project"))
        return p
    except Exception as e:
        print(e)


def get_collection(value):
    for x in Blocks.COLLECTION_CHOICES:
        if value.lower() == x[1].lower():
            return x[0]
    return Blocks.SCRAPE

def get_p_stage(value):
    for x in Blocks.P_STAGE_TYPES:
        if value.lower() == x[1].lower():
            return x[0]
    return

def get_prim(value):
    for x in Blocks.PRIM_TYPES:
        if value.lower() == x[1].lower():
            return x[0]
    return


def get_or_create_blocks(fields:dict):
    try:
        block = Blocks.objects.get(name=fields.get("Block_ID"))
        if fields.get("Pat_ID", []):
            block.patient = get_pat_id(fields.get("Pat_ID",""))
        if fields.get("Assigned Project",[]):
            block.project = get_project_id(fields.get("Assigned Project",[]))
        block.slides = fields.get("Slides",None)
        block.slides_left = fields.get("Slides left",None)
        block.fixation = fields.get("Fixation",None)
        block.collection = get_collection(fields.get("Collection Method",""))
        block.diagnosis = fields.get("Diagnosis",None)
        block.save()
        print("saved")
    except Exception as e:
        print(e)


def _create_blocks_airtable():
    from pyairtable import Api
    api = Api('keyEDswuVpUGOz8Tp')
    t = api.table("appA7qA5hhuLgiAwt", "tblv5WQXW7cNCbt0o")
    for i in t.all():
        get_or_create_blocks(i.get("fields"))


def _pat_get_or_create_consolidated(row):
    try:
        # print(row)
        b = Blocks.objects.filter(name=row["Block"]).update(
            age=None if pd.isnull(row["pat_age"] ) else float(row["pat_age"]),
            thickness=row["thickness"] or "",
            mitoses=None if pd.isnull(row["mitoses"]) else int(row["mitoses"]),
            p_stage=row["p_stage"] or "",
            prim=row["prim"] or "",
            subtype=row["subtype"] or "",
        )
        # b.notes = row["Notes/Other"]
        # b.save()
        print("saved")
    except Exception as e:
        print(e)

def _create_blocks_consolidated_data():
    import pandas as pd
    from pathlib import Path
    file = Path(Path(__file__).parent.parent / "uploads" / "Consolidated_data_final.csv")
    df = pd.read_csv(file)
    df.apply(lambda row: _pat_get_or_create_consolidated(row), axis=1)

def get_or_create_blocks_from_file(row):
    try:
        print(row["Block_ID"])
        ulcreation = True if row["Ulceration"] == "Present" else False if row["Ulceration"] == "negative" else None
        Blocks.objects.filter(name=row["Block_ID"]).update(
            fixation=row["Fixation"],
            slides=int(row["Slides"]) if not pd.isnull(row["Slides"]) else None,
            slides_left=int(row["Slides left"]) if not pd.isnull(row["Slides left"]) else None,
            ulceration=ulcreation,
            collection=get_collection(row["Collection Method"]) if not pd.isnull(row["Collection Method"]) else ""
        )
        print("saved")
    except Exception as e:
        print("error"*10,e)


def get_or_create_bl(row):
    # try:
    print(row["name"])
    try:
        Blocks.objects.create(name=row["name"])
    except:
        print("")
    Blocks.objects.filter(name=row["name"]).update(
        age=row["pat_age"],
        thickness=row["thickness"],
        mitoses=int(row["mitoses"]) if not pd.isnull(row["mitoses"]) else None,
        p_stage=get_p_stage(row["p_stage"]) if not pd.isnull(row["p_stage"]) else None,
        prim=get_p_stage(row["prim"]) if not pd.isnull(row["prim"]) else None,
        subtype=row["subtype"],
        diagnosis=row["dx_text"],
        notes=row["note"],
        micro=row["micro"],
        path_note=row["Path Number"]
    )
    print("saved")
    # except Exception as e:
    #     print("error"*10,e)



def _create_blocks_from_file():
    file = Path(Path(__file__).parent.parent / "uploads" / "Blocks-Grid view-5.csv")
    df = pd.read_csv(file)
    df.apply(lambda row: get_or_create_blocks_from_file(row), axis=1)

#
# def _create_blocks_from_file():
#     file = Path(Path(__file__).parent.parent / "uploads" / "report-block.csv")
#     df = pd.read_csv(file)
#     df = df.apply(lambda row: get_or_create_bl(row), axis=1)
#     df.to_csv("report_matching_sample_lib.csv", index=False)
