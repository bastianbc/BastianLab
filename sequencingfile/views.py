from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async
from .models import SequencingFile
from .serializers import SequencingFileSerializer
from django.http import JsonResponse
from .forms import SequencingFileForm
from django.contrib import messages
import json

@permission_required("sequencingfile.view_sequencingfile",raise_exception=True)
def sequencingfiles(request):
    return render(request, "sequencingfile_list.html", locals())

@permission_required_for_async("sequencingfile.view_sequencingfile")
def filter_sequencingfiles(request):
    sequencingfiles = SequencingFile().query_by_args(request.user,**request.GET)
    serializer = SequencingFileSerializer(sequencingfiles['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = sequencingfiles['draw']
    result['recordsTotal'] = sequencingfiles['total']
    result['recordsFiltered'] = sequencingfiles['count']

    return JsonResponse(result)

@permission_required("sequencingfile.add_sequencingfile",raise_exception=True)
def new_sequencingfile(request):
    if request.method=="POST":
        form = SequencingFileForm(request.POST)
        if form.is_valid():
            sequencingfile = form.save()
            messages.success(request,"Sequencing File %s created successfully." % sequencingfile.folder_name)
            return redirect("sequencingfiles")
        else:
            messages.error(request,"Sequencing File could not be created.")
    else:
        form = SequencingFileForm()

    return render(request,"sequencingfile.html",locals())

@permission_required("sequencingfile.change_sequencingfile",raise_exception=True)
def edit_sequencingfile(request,id):
    sequencingfile = SequencingFile.objects.get(id=id)

    if request.method=="POST":
        form = SequencingFileForm(request.POST,instance=sequencingfile)
        if form.is_valid():
            sequencingfile = form.save()
            messages.success(request,"Sequencing File %s updated successfully." % sequencingfile.folder_name)
            return redirect("sequencingfiles")
        else:
            messages.error(request,"Sequencing File could not be updated!")
    else:
        form = SequencingFileForm(instance=sequencingfile)

    return render(request,"sequencingfile.html",locals())

@permission_required("sequencingfile.delete_sequencingfile",raise_exception=True)
def delete_sequencingfile(request,id):
    try:
        sequencingfile = SequencingFile.objects.get(id=id)
        sequencingfile.delete()
        messages.success(request,"Sequencing File %s deleted successfully." % sequencingfile.name)
        deleted = True
    except Exception as e:
        messages.error(request, "Sequencing File could not be deleted!")
        deleted = False

    return JsonResponse({"deleted":deleted })

@permission_required("sequencingfile.delete_sequencingfile",raise_exception=True)
def delete_batch_sequencingfiles(request):
    try:
        selected_ids = json.loads(request.GET.get("selected_ids"))
        SequencingFile.objects.filter(id__in=selected_ids).delete()
    except Exception as e:
        print(str(e))
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

@permission_required_for_async("sequencingfile.sequencingfile_blocks")
def check_can_deleted_async(request):
    id = request.GET.get("id")
    instance = SequencingFile.objects.get(id=id)
    related_objects = []
    for field in instance._meta.related_objects:
        relations = getattr(instance,field.related_name)
        if relations.count() > 0:
            related_objects.append({
                "model": field.related_model.__name__,
                "count": relations.count()
            })

    return JsonResponse({"related_objects":related_objects})
