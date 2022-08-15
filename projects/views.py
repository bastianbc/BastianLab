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

