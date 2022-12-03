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

@permission_required("librep.view_nucacids",raise_exception=True)
def nucacids(request):
    form = SampleLibCreationOptionsForm()
    return render(request, "nucacid_list.html", locals())

@login_required
def filter_nucacids(request):
    from .serializers import NucacidsSerializer

    nucacids = NucAcids().query_by_args(request.user,**request.GET)
    serializer = NucacidsSerializer(nucacids['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = nucacids['draw']
    result['recordsTotal'] = nucacids['total']
    result['recordsFiltered'] = nucacids['count']

    return JsonResponse(result)

@permission_required("librep.change_nucacids",raise_exception=True)
def edit_nucacid_async(request):
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

    nucacid = custom_update(NucAcids,pk=parameters["pk"],parameters=parameters)

    nucacid.set_init_volume()

    return JsonResponse({"result":True})

@permission_required("librep.add_nucacids",raise_exception=True)
def new_nucacid(request):
    if request.method=="POST":
        print("++++++++++++++++++++++++++++")
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

@permission_required("librep.add_nucacids",raise_exception=True)
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

@permission_required("librep.change_nucacids",raise_exception=True)
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

@permission_required("librep.delete_nucacids",raise_exception=True)
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

@permission_required("librep.delete_nucacids",raise_exception=True)
def delete_batch_nucacids(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        NucAcids.objects.filter(nu_id__in=selected_ids).delete()
    except Exception as e:
        print(str(e))
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })
