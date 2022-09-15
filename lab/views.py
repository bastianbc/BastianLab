from typing import Any
from django.shortcuts import render, redirect, HttpResponse
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
from django.forms.models import inlineformset_factory

from django.forms import Textarea
from django.views.generic.detail import SingleObjectMixin
from .forms import PatientsBlocksWithAreasFormset
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView
from .models import Patients
from .forms import PatientForm, PatientsBlocksWithAreasFormset
import json
from django.http import JsonResponse

class PatientCreate(SuccessMessageMixin, CreateView):
    model = Patients
    template_name_suffix = '_add_form'
    form_class = PatientForm
    # class Meta:
    success_message = "Patient %(pat_id)s was created successfully"
    success_url = reverse_lazy('patients-list')

    # def your_view(request):
    #     form = YourForm(request.POST or None)
    # success = False
    # if request.method == 'POST':
    #     if form.is_valid():
    #         form.save()
    #         form = YourForm()
    #         success = True
    # return render(request, 'your_template.html', {'form': form})

    # def form_valid(self, form):
    #     messages.add_message(
    #         self.request,
    #         messages.SUCCESS,
    #         'The patient %(pat_id) was added.'
    #     )
    #     return render('patients_add_form.html', {'form': form})
class PatientUpdate(SuccessMessageMixin, UpdateView):
    model = Patients
    form_class = PatientForm
    template_name_suffix = '_update_form'
    success_message = 'Patient updated sucessfully'
    success_url = reverse_lazy('patients-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk=self.kwargs.get('pk','')
        patient_object=Patients.objects.get(pa_id=pk)
        blockcount=patient_object.blocks_set.count()
        context['blockcount']=blockcount
        # This is done to display the project abbreviation as a header of the list of blocks
        return context
class PatientDelete(DeleteView):
    model = Patients
    # form_class = PatientForm
    template_name = 'lab/patients_confirm_delete.html'
    success_message = 'Patient deleted sucessfully'
    # fields = ['pat_id','sex','race','source','project','notes']
    success_url = reverse_lazy('patients-list')

    # def delete(self, request, *args, **kwargs):
    #     messages.success(self.request, self.success_message)
    # #     return super(PatientDelete, self).delete(request, *args, **kwargs)

    # def get_context_data(self, **kwargs):
    #     context = super(PatientDelete, self).get_context_data(**kwargs)
    #     print(context)


    # def get_object(self, queryset=None):
    #     """ Hook to ensure object is owned by request.user. """
    #     obj = super(PatientDelete, self).get_object()
    #     if not obj.owner == self.request.user:
    #         raise Http404
    #     assert False
    #     return obj

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

def patients(request):
    return render(request,"patient_list.html")

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

# class PatientView(DetailView):
#     model = Patients
#     context_object_name = 'patient'
#     template_name_suffix = '_detail'
#     # def get_context_data(self, **kwargs):
#     #     context = super(PatientView, self).get_context_data(**kwargs)
#     #     context['page_list'] = Page.objects.all()
#     #     return context


class PatientsBlocksUpdateView(SingleObjectMixin, FormView):
    # For adding blocks to a patient, or editing them.

    model = Patients
    template_name = 'lab/patients_blocks_update.html'

    def get(self, request, *args, **kwargs):
        # The Patient we're editing:
        self.object = self.get_object(queryset=Patients.objects.all())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # The Patient we're uploading for:
        self.object = self.get_object(queryset=Patients.objects.all())
        print(self, request, args, kwargs)
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        # Use our big formset of formsets, and pass in the Patients object.
        return PatientsBlocksWithAreasFormset(
                            **self.get_form_kwargs(), instance=self.object)

    def form_valid(self, form):
        # If the form is valid, redirect to the success URL.
        form.save()

        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Changes were saved.'
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('block-update', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        return context
        #return render(request, "patients-list", context)




# BlockFormset = inlineformset_factory(
#     Patients, Blocks, fields=('old_block_id', 'body_site')
# )

# class PatientBlockCreate(CreateView):
#     template_name = 'lab/patients_add_form.html'
#     model = Patients
#     fields = ["pat_id", 'sex', 'race', 'source', 'project']

#     def get_context_data(self, **kwargs):
#         # we need to overwrite get_context_data
#         # to make sure that our formset is rendered
#         data = super().get_context_data(**kwargs)
#         if self.request.POST:
#             data["blocks"] = BlockFormset(self.request.POST)
#         else:
#             data["blocks"] = BlockFormset()
#         print(data)
#         return data

#     def form_valid(self, form):
#         context = self.get_context_data()
#         blocks = context["blocks"]
#         self.object = form.save()
#         if blocks.is_valid():
#             blocks.instance = self.object
#             blocks.save()
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse("patients-list")

# class PatientsBlockUpdate(UpdateView):
#     model = Patients
#     fields = ["pat_id", 'sex', 'race', 'source', 'notes', 'project']
#     template_name = 'lab/patients_add_form.html'

#     def get_context_data(self, **kwargs):
#         # we need to overwrite get_context_data
#         # to make sure that our formset is rendered.
#         # the difference with CreateView is that
#         # on this view we pass instance argument
#         # to the formset because we already have
#         # the instance created
#         data = super().get_context_data(**kwargs)
#         if self.request.POST:
#             data["blocks"] = BlockFormset(self.request.POST, instance=self.object)
#         else:
#             data["blocks"] = BlockFormset(instance=self.object)
#             patient = data.get('object')
#             data['blocklist'] = Blocks.objects.filter(pat_id=patient)
#         print(data)
#         # assert False
#         return data

#     def form_valid(self, form):
#         context = self.get_context_data()
#         blocks = context["blocks"]
#         self.object = form.save()
#         if blocks.is_valid():
#             blocks.instance = self.object
#             blocks.save()
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse("patients-list")






# from django.contrib import messages
# from django.http import HttpResponseRedirect
# from django.shortcuts import render
# from django.urls import reverse
# from django.views.generic import (
#     CreateView, DetailView, FormView, ListView, TemplateView
# )
# from django.views.generic.detail import SingleObjectMixin

# from .forms import PublisherBooksWithImagesFormset
# from .models import Publisher, Book, BookImage


# class HomeView(TemplateView):
#     template_name = 'books/home.html'


# class PublisherListView(ListView):
#     model = Publisher
#     template_name = 'books/publisher_list.html'


# class PublisherDetailView(DetailView):
#     model = Publisher
#     template_name = 'books/publisher_detail.html'
