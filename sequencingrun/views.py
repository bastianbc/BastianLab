import re
import time
from collections import Counter, namedtuple
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import permission_required
from .serializers import *
from sequencinglib.models import *
from .forms import *
from django.contrib import messages
from core.decorators import permission_required_for_async
from samplelib.models import SampleLib
from samplelib.serializers import SingleSampleLibSerializer
from sequencingfile.models import SequencingFile,SequencingFileSet
import sequencingrun.helper as helper
from django.core.files.base import ContentFile
from capturedlib.models import SL_CL_LINK
import json
from analysisrun.forms import AnalysisRunForm
from sheet.api import _get_authorizated_queryset
from sheet.service import CustomSampleLibSerializer

@permission_required("sequencingrun.view_sequencingrun",raise_exception=True)
def sequencingruns(request):
    form = AnalysisRunForm(initial={"user":request.user})
    return render(request, "sequencingrun_list.html", locals())

@permission_required_for_async("sequencingrun.view_sequencingrun")
def filter_sequencingruns(request):
    sequencingruns = SequencingRun().query_by_args(request.user,**request.GET)
    serializer = SequencingRunSerializer(sequencingruns['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = sequencingruns['draw']
    result['recordsTotal'] = sequencingruns['total']
    result['recordsFiltered'] = sequencingruns['count']

    return JsonResponse(result)

@permission_required_for_async("sequencingrun.change_sequencingrun")
def edit_sequencingrun_async(request):
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
        custom_update(SequencingRun,pk=parameters["pk"],parameters=parameters)
    except Exception as e:
        print(e)
        return JsonResponse({"success":False, "message": str(e)})

    return JsonResponse({"success":True})

@permission_required("sequencingrun.add_sequencingrun",raise_exception=True)
def new_sequencingrun(request):
    if request.method=="POST":
        form = SequencingRunForm(request.POST)
        if form.is_valid():
            sequencingrun = form.save()
            messages.success(request,"Sequencing Run %s created successfully." % sequencingrun.name)
            return redirect("sequencingruns")
        else:
            messages.error(request,"Sequencing Run could not be created.")
    else:
        form = SequencingRunForm()

    return render(request,"sequencingrun.html",locals())

@permission_required_for_async("sequencingrun.add_sequencingrun")
def new_sequencingrun_async(request):

    selected_ids = json.loads(request.GET.get("selected_ids"))
    options = json.loads(request.GET.get("options"))

    try:
        prefixies = SequencingRun.objects.filter(name__startswith=options["prefix"])
        autonumber = 1
        if prefixies.exists():
            max_value = max([int(p.name.split("-")[-1]) for p in prefixies])
            autonumber = max_value + 1
        sequencing_run = SequencingRun.objects.create(
            name="%s-%d" % (options["prefix"],autonumber),
            date=options["date"],
            date_run=options["date_run"],
            facility=options["facility"],
            sequencer=options["sequencer"],
            pe=options["pe"],
            amp_cycles=options["amp_cycles"],
        )

        sequencinglibs = SequencingLib.objects.filter(id__in=selected_ids)

        for sequencing_lib in sequencinglibs:
            sequencing_run.sequencing_libs.add(sequencing_lib)

    except Exception as e:
        print(str(e))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True, "id":sequencing_run.id})

@permission_required("sequencingrun.change_sequencingrun",raise_exception=True)
def edit_sequencingrun(request,id):
    sequencing_run = SequencingRun.objects.get(id=id)

    if request.method=="POST":
        form = SequencingRunForm(request.POST,instance=sequencing_run)
        if form.is_valid():
            form.save()
            messages.success(request,"Sequencing Run %s updated successfully." % sequencing_run.name)
            return redirect("sequencingruns")
        else:
            messages.error(request,"Sequencing Run could not be updated!")
    else:
        form = SequencingRunForm(instance=sequencing_run)

    return render(request,"sequencingrun.html",locals())

@permission_required("sequencingrun.delete_sequencingrun",raise_exception=True)
def delete_sequencingrun(request,id):
    try:
        sequencing_run = SequencingRun.objects.get(id=id)
        sequencing_run.delete()
        messages.success(request,"Sequencing Run %s deleted successfully." % sequencing_run.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Sequencing Run could not be deleted!")
        deleted = False

    return JsonResponse({"deleted":deleted })

@permission_required("sequencingrun.delete_sequencingrun",raise_exception=True)
def delete_batch_sequencingruns(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        SequencingRun.objects.filter(id__in=selected_ids).delete()
    except Exception as e:
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

@permission_required("sequencingrun.view_sequencingrun",raise_exception=True)
def get_used_sequencinglibs(request,id):
    sequencing_run = SequencingRun.objects.get(id=id)
    used_sequencinglibs = sequencing_run.sequencing_libs.all()
    serializer = UsedSequencingLibSerializer(used_sequencinglibs, many=True)
    return JsonResponse(serializer.data, safe=False)

@permission_required_for_async("blocks.delete_blocks")
def check_can_deleted_async(request):
    id = request.GET.get("id")
    instance = SequencingRun.objects.get(id=id)
    related_objects = []
    for field in instance._meta.related_objects:
        relations = getattr(instance,field.related_name)
        if relations.count() > 0:
            related_objects.append({
                "model": field.related_model.__name__,
                "count": relations.count()
            })

    return JsonResponse({"related_objects":related_objects})

def get_facilities(request):
    return JsonResponse([{"label":"---------","value":""}] + [{ "label":c[1], "value":c[0] } for c in SequencingRun.FACILITY_TYPES], safe=False)

def get_sequencers(request):
    return JsonResponse([{"label":"---------","value":""}] + [{ "label":c[1], "value":c[0] } for c in SequencingRun.SEQUENCER_TYPES], safe=False)

def get_pes(request):
    return JsonResponse([{"label":"---------","value":""}] + [{ "label":c[1], "value":c[0] } for c in SequencingRun.PE_TYPES], safe=False)

def add_async(request):
    try:
        seq_run_id = request.GET["id"]
        selected_ids = json.loads(request.GET.get("selected_ids"))
        sequencing_run = SequencingRun.objects.get(id=seq_run_id)
        sequencinglibs = SequencingLib.objects.filter(id__in=selected_ids)
        for sequencing_lib in sequencinglibs:
            sequencing_run.sequencing_libs.add(sequencing_lib)
        return JsonResponse({"success":True})
    except Exception as e:
        return JsonResponse({"success":False, "message": str(e)})

def get_sequencing_files(request, id):
    try:
        sequencing_run = SequencingRun.objects.get(id=id)
        sample_libs = SampleLib.objects.filter(sl_cl_links__captured_lib__cl_seql_links__sequencing_lib__sequencing_runs=sequencing_run).distinct().order_by('name')
        file_sets = helper.get_file_sets(sequencing_run, sample_libs)
        return JsonResponse({
            'success': True,
            "file_sets": file_sets,
            "sample_libs": SingleSampleLibSerializer(sample_libs, many=True).data,
            "sequencing_run": SingleSequencingRunSerializer(sequencing_run).data
        })
    except Exception as e:
        print("$"*100)
        return JsonResponse({"success": False, "message": str(e)})

def save_sequencing_files(request, id):
    # try:
        sequencing_run = SequencingRun.objects.get(id=id)
        sample_libs = SampleLib.objects.filter(
            sl_cl_links__captured_lib__cl_seql_links__sequencing_lib__sequencing_runs=sequencing_run
        ).distinct().order_by('name')
        data = json.loads(request.POST.get('data'))
        print("*"*100, data)
        # files from source directory
        file_sets = helper.get_file_sets(sequencing_run, sample_libs)
        print("1"*10)

        print(file_sets)
        files_created = helper.create_files_and_sets(file_sets, sequencing_run)
        print(files_created)
        if files_created:
            return JsonResponse({"success": True, "data": files_created})
        else:
            return JsonResponse({"success": False})
    # except Exception as e:
    #     return JsonResponse({"success": False, "message": str(e)})
    # return JsonResponse({"success": success})

def get_sample_libs_async(request):
    """
    Provides the data needed to generate an analysis sheet. Returns a list that the sequencing run and the sample libraries that belong to it.
    It can be worked on multiple sequencing runs selected by a user.
    # Parameters:
    selected_ids: List of Ids of selected and pushed sequencing runs.
    # Returns:
    A list data formatted according to purpose.
    """
    selected_ids = json.loads(request.GET.get("selected_ids"))
    sequencing_runs = SequencingRun.objects.filter(id__in=selected_ids)
    qs=_get_authorizated_queryset(sequencing_runs)
    serializer = CustomSampleLibSerializer(qs, many=True)
    result = dict()
    result['data'] = serializer.data
    return JsonResponse(serializer.data, safe=False)
    # selected_sequencing_runs = SequencingRun.objects.filter(id__in=selected_ids).prefetch_related('sequencing_libs')
    # # Function to get the related sequencing files for each sequencing run
    # def get_sequencing_files(sequencing_file_set):
    #     files = SequencingFile.objects.filter(sequencing_file_set=sequencing_file_set).values('name', 'checksum')
    #     return {file['name']: file['checksum'] for file in files}
    #
    # data = []
    #     @patient = serializers.CharField(read_only=True)
    #     @seq_run = serializers.SerializerMethodField()
    #     @na_type = serializers.CharField(read_only=True)
    #     @bait = serializers.CharField(read_only=True)
    #     @area_type = serializers.CharField(read_only=True)
    #     @matching_normal_sl = serializers.CharField(read_only=True)
    #     @barcode_name = serializers.CharField(read_only=True)
    #     fastq = serializers.CharField(read_only=True)
    #     bam = serializers.CharField(read_only=True)
    #     bai = serializers.CharField(read_only=True)
    #     path_fastq = serializers.CharField(read_only=True)
    #     path_bam = serializers.CharField(read_only=True)
    #     path_bai = serializers.CharField(read_only=True)
    # for seq_run in selected_sequencing_runs:
    #     item = {
    #         'patient': '',
    #         'sample_lib': '',
    #         'barcode': '',
    #         'na_type': '',
    #         'area_type': '',
    #         'sequencing_run': '',
    #         'footprint': '',
    #         'file': '',
    #         'path': '',
    #         'matching_normal_sl': '',
    #         'err':'',
    #     }
    #     for sequencing_file_set in seq_run.sequencing_file_sets.all():
    #         print(sequencing_file_set)
    #         item["sequencing_run"] = seq_run.name
    #
    #         sample_lib = sequencing_file_set.sample_lib
    #         if sample_lib:
    #             item["sample_lib"] = sample_lib.name
    #             item["barcode"] = sample_lib.barcode.name if sample_lib.barcode else ""
    #
    #             na_sl_link = sample_lib.na_sl_links.first()
    #             if na_sl_link:
    #                 nuc_acid = na_sl_link.nucacid
    #                 item["na_type"] = nuc_acid.na_type
    #
    #                 area_na_link = nuc_acid.area_na_links.first()
    #                 if area_na_link:
    #                     area = area_na_link.area
    #                     item["area_type"] = area.area_type.value
    #
    #                     patient = area.block.patient
    #
    #                     # The patients who has sample libraries that area type is "Normal"
    #                     matching_normal_sl = []
    #                     if patient:
    #                         normal_sample_libs = SampleLib.objects.filter(na_sl_links__nucacid__area_na_links__area__block__patient=patient,
    #                                                                       na_sl_links__nucacid__area_na_links__area__area_type__value='normal')
    #                         matching_normal_sl = list(normal_sample_libs.values_list('name', flat=True))
    #
    #                         item["patient"] = patient.pat_id
    #                         item["matching_normal_sl"] = matching_normal_sl
    #                     else:
    #                         item["err"] = "not found patient"
    #                 else:
    #                     item["err"] = "not found area_na_link"
    #             else:
    #                 item["err"] = "not found na_sl_link"
    #
    #             if sample_lib.sl_cl_links is not None:
    #                 sl_cl_link = sample_lib.sl_cl_links.first()
    #
    #                 if sl_cl_link:
    #                     captured_lib = sl_cl_link.captured_lib
    #                     item["footprint"] = captured_lib.bait.name
    #                 else:
    #                     item["err"] = "not found sl_cl_link"
    #             else:
    #                 item["err"] = "not found sl_cl_links of a sample_lib"
    #         else:
    #             item["err"] = "not found samplelib"
    #
    #
    #         item["files"] = get_sequencing_files(sequencing_file_set)
    #         item["path"] = sequencing_file_set.path if sequencing_file_set.path else f"HiSeqData/{seq_run.name}"
    #
    #         data.append(item)


    print("$"*100, data)
    return JsonResponse(data, safe=False)
