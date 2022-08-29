from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect

from django.core.paginator import Paginator, EmptyPage,\
                                  PageNotAnInteger
from django.db.models import Q
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView

from django.forms import Textarea
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Projects
from .forms import ProjectForm

def filter_projects(request):
    from .serializers import ProjectsSerializer
    from django.http import JsonResponse

    projects = Projects().query_by_args(**request.GET)
    serializer = ProjectsSerializer(projects['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = projects['draw']
    result['recordsTotal'] = projects['total']
    result['recordsFiltered'] = projects['count']

    return JsonResponse(result)

def projects(request):
    return render(request,"project_list.html")

def new_project(request):
    if request.method=="POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request,"Project %s was created successfully." % project.pat_id)
            return redirect("projects")
        else:
            messages.error(request,"Project wasn't created.")
    else:
        form = ProjectForm()

    return render(request,"project.html",locals())

def edit_project(request,id):
    project = projects.objects.get(pat_id=id)

    if request.method=="POST":
        form = ProjectForm(request.POST,instance=project)
        if form.is_valid():
            project = form.save()
            messages.success(request,"Project %s was updated successfully." % project.pat_id)
            return redirect("projects")
        else:
            messages.error(request,"Project wasn't updated!")
    else:
        form = ProjectForm(instance=project)

    return render(request,"project.html",locals())

def delete_project(request,id):
    try:
        project = projects.objects.get(pat_id=id)
        project.delete()
        messages.success(request,"Project %s was deleted successfully." % project.pat_id)
        deleted = True
    except Exception as e:
        messages.error(request, "Project %s wasn't deleted!" % project.pat_id)
        deleted = False

    return JsonResponse({ "deleted":True })

class ProjectCreate(SuccessMessageMixin, CreateView):
    model = Projects
    template_name_suffix = '_add_form'
    form_class = ProjectForm
    # class Meta:
    success_message = "Project was created successfully"
    success_url = reverse_lazy('projects-list')

class ProjectUpdate(SuccessMessageMixin, UpdateView):
    model = Projects
    form_class = ProjectForm
    template_name_suffix = '_update_form'
    success_message = 'Project updated sucessfully'
    success_url = reverse_lazy('projects-list')



class ProjectDelete(DeleteView):
    model = Projects
    # form_class = ProjectForm
    template_name_suffix = '_confirm_delete'
    success_message = 'Project deleted sucessfully'
    # fields = ['pat_id','sex','race','source','project','notes']
    success_url = reverse_lazy('projects-list')


class ProjectList(ListView):
    model = Projects
    template_name_suffix = '_list'
    context_object_name = 'all_projects'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # print(context)
        context['query'] = self.request.GET.get('q')
        #print(context)
        # magical = context.get('object_list')
        # print(magical)
        return context

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = Projects.objects.all().order_by('abbreviation')
        # print('Hello')
        if query:
            object_list = Projects.objects.filter(
            Q(description__icontains=query) | Q(name__icontains=query
            ) |Q(abbreviation__icontains=query)
            ).order_by('abbreviation')
        # print(object_list)
        return object_list
