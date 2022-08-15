from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.core.paginator import Paginator, EmptyPage,\
                                  PageNotAnInteger
from django.db.models import Q 
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Patients, Blocks, Areas
from pages.models import Page
from .forms import PatientForm
from django.contrib.messages.views import SuccessMessageMixin


class PatientList(ListView):
    model = Patients
    template_name = 'lab/patients_list2.html'
    context_object_name = 'all_patients'
    paginate_by = 12

    # def get_context_data(self, **kwargs):
    #     context = super(PatientList, self).get_context_data(**kwargs)
    #     context['page_list'] = Page.objects.all()
    #     return context

class PatientView(DetailView):
    model = Patients
    context_object_name = 'patient'
    template_name_suffix = '_detail'
    # def get_context_data(self, **kwargs):
    #     context = super(PatientView, self).get_context_data(**kwargs)
    #     context['page_list'] = Page.objects.all()
    #     return context

class PatientSearch(ListView):
    model = Patients
    template_name = 'lab/patients_list2.html'
    queryset = Patients.objects.all()
    #queryset = Patients.objects.filter(source__icontains = 'Z')
    context_object_name = 'all_patients'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = Patients.objects.all().order_by('pat_id')
        # print('Hello')
        if query:
            object_list = Patients.objects.filter(
            Q(source__icontains=query) | Q(project__icontains=query)
        ).order_by('pat_id')
        
        paginator = Paginator(object_list, 12) # 6 posts per page
        page = self.request.GET.get('page')

        try:
            object_list = paginator.page(page)
        except PageNotAnInteger:
            object_list = paginator.page(1)
        except EmptyPage:
            object_list = paginator.page(paginator.num_pages)
        return object_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        return context
        # return render(request, "post-list.html", context)

    # def get_queryset(self, **kwargs):
    #     try:
    #         source = self.kwargs['source']
    #     except:
    #         source = ''
    #     if (source != ''):
    #         object_list = self.model.objects.filter(name__icontains = source)
    #     else:
    #         object_list = self.model.objects.all()
    #     return object_list



def get_name(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'lab/name.html', {'form': form})

def get_patient(request):
    submitted = False
    assert False
    if request.method == 'POST':
        form = TpatsForm(request.POST)
        #assert False
        if form.is_valid():
            #assert False
            form.save()
            return HttpResponseRedirect('/lab/addpatient/?submitted=True')
    else:
        form=TpatsForm()
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'lab/patient.html', {'form': form, 'submitted': submitted})

class PatientCreate(CreateView):
    model = Patients
    fields = ['pat_id','sex','race','source','project','notes']
    template_name_suffix = '_add_form'
    success_message = "%(pat_id)s was created successfully"
    success_url = reverse_lazy('patients-list')

class PatientUpdate(SuccessMessageMixin, UpdateView):
    model = Patients
    fields = ['pat_id', 'sex', 'race', 'source', 'project', 'notes']
    template_name_suffix = '_update_form'
    success_message = 'Patient updated sucessfully'
    success_url = reverse_lazy('patients-list')
    

class PatientDelete(SuccessMessageMixin, DeleteView):
    model = Patients
    template_name_suffix = '_confirm_delete'
    success_message = 'Patient deleted sucessfully'
    fields = ['pat_id','sex','race','source','project','notes']
    success_url = reverse_lazy('patients-list')
    #assert False
    # def get_object(self, queryset=None):
    #     """ Hook to ensure object is owned by request.user. """
    #     obj = super(PatientDelete, self).get_object()
    #     if not obj.owner == self.request.user:
    #         raise Http404
    #     return obj
    

    
