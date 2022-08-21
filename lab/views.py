from typing import Any
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
from django.forms.models import inlineformset_factory

from django.forms import Textarea
from django.views.generic.detail import SingleObjectMixin
from .forms import PatientsBlocksWithAreasFormset
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView
from .models import Patients, Blocks, Areas
from .forms import PatientForm, PatientsBlocksWithAreasFormset


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

class PatientList(ListView):
    model = Patients
    template_name = 'lab/patients_list2.html'
    context_object_name = 'all_patients'
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
        object_list = Patients.objects.all().order_by('-date_added')
        # print('Hello')
        if query:
            object_list = Patients.objects.filter(
            Q(source__icontains=query) | Q(project__icontains=query
            ) |Q(pat_id__icontains=query)
            ).order_by('pa_id')
        # print(object_list)
        return object_list


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




BlockFormset = inlineformset_factory(
    Patients, Blocks, fields=('old_block_id', 'body_site')
)
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
