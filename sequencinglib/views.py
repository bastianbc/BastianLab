from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required,permission_required
from .serializers import *
from .models import *
from .forms import *
from django.contrib import messages
from capturedlib.models import *
from sequencingrun.forms import *
from datetime import datetime
from core.decorators import permission_required_for_async

@permission_required("sequencinglib.view_sequencinglib",raise_exception=True)
def sequencinglibs(request):
    form = SequencingRunCreationForm()
    form_seq_run_add = SequencingLibAddForm()
    return render(request, "sequencinglib_list.html", locals())

@permission_required_for_async("sequencinglib.view_sequencinglib")
def filter_sequencinglibs(request):
    sequencinglibs = SequencingLib().query_by_args(request.user,**request.GET)
    serializer = SequencingLibSerializer(sequencinglibs['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = sequencinglibs['draw']
    result['recordsTotal'] = sequencinglibs['total']
    result['recordsFiltered'] = sequencinglibs['count']

    return JsonResponse(result)

@permission_required_for_async("sequencinglib.change_sequencinglib")
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

    try:
        custom_update(SequencingLib,pk=parameters["pk"],parameters=parameters)
    except Exception as e:
        return JsonResponse({"success":False, "message": str(e)})

    return JsonResponse({"success":True})

@permission_required("sequencinglib.add_sequencinglib",raise_exception=True)
def new_sequencinglib(request):
    if request.method=="POST":
        form = SequencingLibForm(request.POST, request.FILES)
        if form.is_valid():
            sequencinglib = form.save()
            messages.success(request,"Captured Library %s created successfully." % sequencinglib.name)
            return redirect("sequencinglibs")
        else:
            messages.error(request,"Captured Library could not be created.")
    else:
        form = SequencingLibForm()

    return render(request,"sequencinglib.html",locals())

@permission_required_for_async("sequencinglib.add_sequencinglib")
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
            buffer=options["buffer"],
            target_vol= float(options["vol_init"]),
            nmol=float(options["nm"]) * float(options["vol_init"])
        )

        for captured_lib in capturedlibs:
            # target_mol = nm * vol
            # CLcount = the number CLs selected
            # Calculate CL_Seq_L_link.volume for each CL using (target_mol/CLcount)/CL.nM

            CL_SEQL_LINK.objects.create(
                sequencing_lib = sequencing_lib,
                captured_lib = captured_lib,
                # volume = ((float(options["nm"]) * float(options["vol_init"])) / len(selected_ids))/captured_lib.nm
            )

    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required_for_async("sequencinglib.view_sequencinglib")
def get_sequencinglib_async(request,id):
    sequencing_lib = SequencingLib.objects.get(id=id)
    serializer = SingleSequencingLibSerializer(sequencing_lib,many=False)
    return JsonResponse(serializer.data, safe=False)

@permission_required_for_async("sequencinglib.add_sequencinglib")
def recreate_sequencinglib_async(request):
    selected_ids = json.loads(request.GET.get("selected_ids"))
    options = json.loads(request.GET.get("options"))

    try:
        sequencing_lib = SequencingLib.objects.get(id=options["sequencing_lib"])
        capturedlibs = CapturedLib.objects.filter(id__in=selected_ids)

        CL_SEQL_LINK.objects.filter(sequencing_lib=sequencing_lib).delete()

        sequencing_lib.nmol = float(options["nm"]) * float(options["vol_init"])
        sequencing_lib.nm = float(options["vol_init"])
        sequencing_lib.save()

        for captured_lib in capturedlibs:
            # target_mol = nm * vol
            # CLcount = the number CLs selected
            # Calculate CL_Seq_L_link.volume for each CL using (target_mol/CLcount)/CL.nM

            CL_SEQL_LINK.objects.create(
                sequencing_lib = sequencing_lib,
                captured_lib = captured_lib,
                volume = ((float(options["nm"]) * float(options["vol_init"])) / len(selected_ids))/captured_lib.nm
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
            messages.success(request,"Captured Library %s updated successfully." % sequencinglib.name)
            return redirect("sequencinglibs")
        else:
            messages.error(request,"Captured Library could not be updated!")
    else:
        form = SequencingLibForm(instance=sequencinglib)

    return render(request,"sequencinglib.html",locals())

@permission_required("sequencinglib.delete_sequencinglib",raise_exception=True)
def delete_sequencinglib(request,id):
    try:
        sequencinglib = SequencingLib.objects.get(id=id)
        sequencinglib.delete()
        messages.success(request,"Captured Library %s deleted successfully." % sequencinglib.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Captured Library could not be deleted!")
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
def make_sequencinglib_async(request,id):
    try:
        values = json.loads(request.GET.get("values"))
        sequencing_lib = SequencingLib.objects.get(id=id)
        for value in values:
            volume = float(value["volume"])

            captured_lib = CapturedLib.objects.get(id=value["id"])

            link = CL_SEQL_LINK.objects.get(sequencing_lib=sequencing_lib,captured_lib=captured_lib)
            link.volume = volume
            link.save()

            captured_lib.update_volume(volume)
    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

def create_ilab_sheet(request):
    import csv
    from django.http import HttpResponse

    class Report(object):
        name = ""
        date = ""
        nmol = 0.0
        buffer = ""
        sample_lib = 0
        i5 = ""
        i7 = ""

    result = []

    for seq_link in CL_SEQL_LINK.objects.all():
        report = Report()
        report.name = seq_link.sequencing_lib.name
        report.date = datetime.strftime(seq_link.sequencing_lib.date,"%m/%d/%Y")
        report.nmol = seq_link.sequencing_lib.nmol
        report.buffer = seq_link.sequencing_lib.get_buffer_display()
        for sl_link in seq_link.captured_lib.sl_cl_links.all():
            report.sample_lib = sl_link.sample_lib.id
            report.i5 = sl_link.sample_lib.barcode.i5 if sl_link.sample_lib.barcode else None
            report.i7 = sl_link.sample_lib.barcode.i7 if sl_link.sample_lib.barcode else None
        result.append(report)

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="sequencinglib.csv"'},
    )

    field_names = ["name","date","nmol","buffer","sample_lib","i5","i7"]
    writer = csv.writer(response)
    writer.writerow(field_names)
    for item in result:
        writer.writerow([getattr(item, field) for field in field_names])

    return response

@permission_required_for_async("blocks.delete_blocks")
def check_can_deleted_async(request):
    id = request.GET.get("id")
    instance = SequencingLib.objects.get(id=id)
    related_objects = []
    for field in instance._meta.related_objects:
        relations = getattr(instance,field.related_name)
        if relations.count() > 0:
            related_objects.append({
                "model": field.related_model.__name__,
                "count": relations.count()
            })

    return JsonResponse({"related_objects":related_objects})

def get_buffers(request):
    return JsonResponse([{"label":"---------","value":""}] + [{ "label":c[1], "value":c[0] } for c in SequencingLib.BUFFER_TYPES], safe=False)
