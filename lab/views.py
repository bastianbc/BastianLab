from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Patients
from .forms import PatientForm
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required,permission_required

# @login_required
def filter_patients(request):
    from .serializers import PatientsSerializer
    from django.http import JsonResponse

    patients = Patients().query_by_args(**request.GET)
    serializer = PatientsSerializer(patients['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = patients['draw']
    result['recordsTotal'] = patients['total']
    result['recordsFiltered'] = patients['count']

    return JsonResponse(result)

# @permission_required("lab.view_patients",raise_exception=True)
def patients(request):
    return render(request,"patient_list.html")

# @permission_required("lab.add_patients",raise_exception=True)
def new_patient(request):
    if request.method=="POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request,"Patient %s was created successfully." % patient.pat_id)
            return redirect("patients")
        else:
            messages.error(request,"Patient wasn't created.")
    else:
        form = PatientForm()

    return render(request,"patient.html",locals())

# @permission_required("lab.change_patients",raise_exception=True)
def edit_patient(request,id):
    patient = Patients.objects.get(pat_id=id)

    if request.method=="POST":
        form = PatientForm(request.POST,instance=patient)
        if form.is_valid():
            patient = form.save()
            messages.success(request,"Patient %s was updated successfully." % patient.pat_id)
            return redirect("patients")
        else:
            messages.error(request,"Patient wasn't updated!")
    else:
        form = PatientForm(instance=patient)

    return render(request,"patient.html",locals())

# @permission_required("lab.change_patients",raise_exception=True)
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

    custom_update(Patients,pk=parameters["pk"],parameters=parameters)

    return JsonResponse({"result":True})

# @permission_required("lab.delete_patients",raise_exception=True)
def delete_patient(request,id):
    try:
        patient = Patients.objects.get(pat_id=id)
        patient.delete()
        messages.success(request,"Patient %s was deleted successfully." % patient.pat_id)
        deleted = True
    except Exception as e:
        messages.error(request, "Patient %s wasn't deleted!" % patient.pat_id)
        deleted = False

    return JsonResponse({ "deleted":True })

def get_race_options(request):
    return JsonResponse([{ "name":race[1], "value":race[0] } for race in Patients.RACE_TYPES], safe=False)

def get_sex_options(request):
    return JsonResponse([{ "name":sex[1], "value":sex[0] } for sex in Patients.SEX_TYPES], safe=False)
