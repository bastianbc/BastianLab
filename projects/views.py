from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Projects
from .forms import ProjectForm
from django.http import JsonResponse
import json
from .serializers import ProjectsSerializer
from django.contrib.auth.decorators import login_required,permission_required

@login_required
def filter_projects(request):

    projects = Projects().query_by_args(request.user,**request.GET)
    serializer = ProjectsSerializer(projects['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = projects['draw']
    result['recordsTotal'] = projects['total']
    result['recordsFiltered'] = projects['count']

    return JsonResponse(result)

@permission_required("projects.view_projects",raise_exception=True)
def projects(request):
    return render(request,"project_list.html")

@permission_required("projects.add_projects",raise_exception=True)
def new_project(request):
    if request.method=="POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request,"Project %s created successfully." % project.pr_id)
            return redirect("projects")
        else:
            messages.error(request,"Project could not be created.")
    else:
        form = ProjectForm()

    return render(request,"project.html",locals())

@permission_required("projects.change_projects",raise_exception=True)
def edit_project(request,id):
    project = Projects.objects.get(pr_id=id)

    if request.method=="POST":
        form = ProjectForm(request.POST,instance=project)
        if form.is_valid():
            project = form.save()
            messages.success(request,"Project %s updated successfully." % project.pr_id)
            return redirect("projects")
        else:
            messages.error(request,"Project could not be updated!")
    else:
        form = ProjectForm(instance=project)

    return render(request,"project.html",locals())

@permission_required("projects.change_projects",raise_exception=True)
def edit_project_async(request):
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
        custom_update(Projects,pk=parameters["pk"],parameters=parameters)
    except Exception as e:
        return JsonResponse({"success":False, "message": str(e)})

    return JsonResponse({"success":True})

@permission_required("projects.delete_projects",raise_exception=True)
def delete_project(request,id):
    try:
        project = Projects.objects.get(pr_id=id)
        project.delete()
        messages.success(request,"Project %s deleted successfully." % project.pr_id)
    except Exception as e:
        messages.error(request, "Project %s could not be deleted!")
        return JsonResponse({ "deleted":False })

    return JsonResponse({ "deleted":True })

def get_pi_options(request):
    return JsonResponse([{"label":"---------","value":""}] + [{ "label":c[1], "value":c[0] } for c in Projects.PI_CHOICES], safe=False)
