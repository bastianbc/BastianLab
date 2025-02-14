from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Patient
from .forms import PatientForm, FilterForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async
from blocks.models import Block
import pandas as pd
import json

@permission_required_for_async("lab.view_patients")
def filter_patients(request):
    from .serializers import PatientsSerializer
    from django.http import JsonResponse
    
    patients = Patient().query_by_args(**request.GET)
    serializer = PatientsSerializer(patients['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = patients['draw']
    result['recordsTotal'] = patients['total']
    result['recordsFiltered'] = patients['count']

    return JsonResponse(result)

@permission_required("lab.view_patients",raise_exception=True)
def patients(request):
    filter = FilterForm()
    return render(request,"patient_list.html", locals())

@permission_required("lab.add_patients",raise_exception=True)
def new_patient(request):
    if request.method=="POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request,"Patient %s created successfully." % patient.pat_id)
            return redirect("patients")
        else:
            messages.error(request,"Patient could not be created.")
    else:
        form = PatientForm()

    return render(request,"patient.html",locals())

@permission_required("lab.change_patients",raise_exception=True)
def edit_patient(request,id):
    patient = Patient.objects.get(id=id)

    if request.method=="POST":
        form = PatientForm(request.POST,instance=patient)
        if form.is_valid():
            patient = form.save()
            messages.success(request,"Patient %s updated successfully." % patient.pat_id)
            return redirect("patients")
        else:
            messages.error(request,"Patient could not be updated!")
    else:
        form = PatientForm(instance=patient)

    return render(request,"patient.html",locals())

@permission_required_for_async("lab.change_patients")
def edit_patient_async(request):
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
        custom_update(Patient,pk=parameters["pk"],parameters=parameters)
    except Exception as e:
        return JsonResponse({"success":False, "message": str(e)})

    return JsonResponse({"success":True})

@permission_required("lab.delete_patients",raise_exception=True)
def delete_patient(request,id):
    try:
        patient = Patient.objects.get(pat_id=id)
        patient.delete()
        messages.success(request,"Patient %s deleted successfully." % patient.pat_id)
        deleted = True
    except Exception as e:
        messages.error(request, "Patient %s could not be deleted!" % patient.pat_id)
        deleted = False

    return JsonResponse({ "deleted":True })

@permission_required("lab.delete_patients",raise_exception=True)
def delete_batch_patients(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        Patient.objects.filter(id__in=selected_ids).delete()
    except Exception as e:
        return JsonResponse({ "deleted":False, "message":str(e) })

    return JsonResponse({ "deleted":True })

def get_race_options(request):
    return JsonResponse([{"label":"---------","value":""}] + [{ "label":c[1], "value":c[0] } for c in Patient.RACE_TYPES], safe=False)

def get_sex_options(request):
    return JsonResponse([{"label":"---------","value":""}] + [{ "label":c[1], "value":c[0] } for c in Patient.SEX_TYPES], safe=False)

def export_csv_all_data(request):
    import csv
    from django.http import HttpResponse

    result = []

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="patients.csv"'},
    )

    field_names = [f.name for f in Patient._meta.fields]
    writer = csv.writer(response)
    writer.writerow(field_names)
    for patient in Patient.objects.all():
        writer.writerow([getattr(patient, field) for field in field_names])

    return response


def get_race(value):
    for x in Patient.RACE_TYPES:
        if value.lower() == x[1].lower():
            return x[0]
    return 7

def _pat_get_or_create(fields:dict):
    try:
        pat = Patient.objects.get(pat_id=fields.get("Pat_ID"))
        pat.sex = fields.get("Gender","")
        pat.race = get_race(fields.get("Race",""))
        pat.source = fields.get("Source","")
        pat.notes = fields.get("Notes","")
        pat.save()
    except Exception as e:
        print(e)

def _patient_get_or_create(value):
    if value:
        obj, created = Patient.objects.get_or_create(
            pat_id=value
        )
        return obj
    return None

def _block_get_or_create(value):
    if value:
        obj, created = Block.objects.get_or_create(
            name=value
        )
        return obj
    return None

def _pat_get_or_create_consolidated(row):
    try:
        b = Block.objects.get(name=row["Block"])
        b.patient = Patient.objects.get(pat_id=str(row["pat_id"]).replace(".0",""))
        b.save()
        print("saved")
    except Exception as e:
        print(e)

def _pat_done_import(row):
    try:
        if not pd.isnull(row["Block"]):
            try:
                Block.objects.get(name=row["Block"])
            except:
                b = Block.objects.create(name=row["Block"])
                patient = _patient_get_or_create(row["pat_id"])
                b.patient = patient
                b.save()
    except Exception as e:
        print(e)

def _cerate_patients_from_consolidated_data():
    import pandas as pd
    from pathlib import Path

    file = Path(Path(__file__).parent.parent / "uploads" / "Consolidated_data_final.csv")
    df = pd.read_csv(file)
    df[~df["pat_id"].isnull()].apply(lambda row: _pat_get_or_create_consolidated(row), axis=1)

def _cerate_patients_from_patients_done():
    import pandas as pd
    from pathlib import Path

    file = Path(Path(__file__).parent.parent / "uploads" / "patients_done.csv")
    df = pd.read_csv(file)
    df.apply(lambda row: _pat_done_import(row), axis=1)
