from django.shortcuts import render, redirect
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
from django.forms.models import inlineformset_factory, modelformset_factory

from django.forms import Textarea, formset_factory, TextInput, DateInput
from .models import NucAcids, SampleLib
from .forms import *
from areas.models import Areas
from blocks import *
from django.utils.http import urlencode
from utils.utils import sorted_nicely
import re
import json
from django.http import JsonResponse

def nucacids(request):
    return render(request, "nucacids.html", locals())

def filter_nucacids(request):
    from .serializers import NucacidsSerializer

    nucacids = NucAcids().query_by_args(**request.GET)
    serializer = NucacidsSerializer(nucacids['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = nucacids['draw']
    result['recordsTotal'] = nucacids['total']
    result['recordsFiltered'] = nucacids['count']

    return JsonResponse(result)

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

    custom_update(NucAcids,pk=parameters["pk"],parameters=parameters)

    return JsonResponse({"result":True})

def new_nucacid(request):
    if request.method=="POST":
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

def new_nucacid_async(request):
    selected_ids = json.loads(request.GET.get("selected_ids"))

    try:
        for id in selected_ids:
            area = Areas.objects.get(ar_id=id)
            NucAcids.objects.create(area=area)
    except Exception as e:
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

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

def delete_nucacid(request,id):
    try:
        nucacid = NucAcids.objects.get(nu_id=id)
        nucacid.delete()
        messages.success(request,"Nucleci Acid %s was deleted successfully." % nucacid.nu_id)
        deleted = True
    except Exception as e:
        messages.error(request, "Nuclecic Acid %s wasn't deleted!" % nucacid.nu_id)
        deleted = False

    return JsonResponse({ "deleted":True })


# def add_nucs_to_area(request, areas_to_add_to, cd):
#     old_na_id=cd.get('prefix')
#     na_type = cd.get('na_type')
#     method = cd.get('method')
#     existing_nucacids=NucAcids.objects.filter(old_na_id__startswith=old_na_id).values_list('old_na_id', flat=True)
#     if existing_nucacids:
#         last_nucacid=sorted_nicely(existing_nucacids)[-1]
#         digits=re.findall(r'\d+', last_nucacid)
#         # Gets a list of the numbers out of the last_area
#         last_nucacid_id = int(digits[-1])
#         # Takes the last number from that list
#     else:
#         last_nucacid_id = 0
#     if areas_to_add_to:
#             selected_areas = Areas.objects.filter(ar_id__in=areas_to_add_to)
#             for area in selected_areas:
#                 last_nucacid_id += 1
#                 if na_type == 'DNA' or na_type == 'RNA':
#                     new_nuc = NucAcids(nu_id=None,
#                                     old_area_id=area.old_area_id,
#                                     area=area,
#                                     method=method,
#                                     na_type=na_type,
#                                     old_na_id=old_na_id+'-'+na_type[0:]+'-'+str(last_nucacid_id)
#                                     )
#                     new_nuc.save()
#                     messages.success(request, 'NucAcid '+str(new_nuc.old_na_id)+' added to Area '
#                                 + area.old_area_id )
#                 else:
#                     # na_type was DNA+RNA, so have to make two NAs
#                     # First make DNA
#                     new_nuc = NucAcids(nu_id=None,
#                                     old_area_id=area.old_area_id,
#                                     area=area,
#                                     na_type='DNA',
#                                     method=method,
#                                     old_na_id=old_na_id+'-D-'+str(last_nucacid_id)
#                                     )
#                     new_nuc.save()
#                     messages.success(request, 'NucAcid '+str(new_nuc.old_na_id)+' added to Area '
#                                 + area.old_area_id )
#                      #   Now make RNA
#                     new_nuc = NucAcids(nu_id=None,
#                                     old_area_id=area.old_area_id,
#                                     area=area,
#                                     na_type='RNA',
#                                     method=method,
#                                     old_na_id=old_na_id+'-R-'+str(last_nucacid_id)
#                                     )
#                     new_nuc.save()
#                     messages.success(request, 'NucAcid '+str(new_nuc.old_na_id)+' added, extracted from Area '
#                                 + area.old_area_id )
#
#     request.session.pop('selected_areas')
#     return
#
# class NucAcidsList(ListView):
#     queryset = NucAcids.objects.all().order_by('-nu_id')
#     template_name = 'libprep/nucacids_datatables.html'
#     context_object_name = 'all_nucacids'
#     # paginate_by = 24
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['query'] = self.request.GET.get('q')
#         current_area = self.request.GET.get('areaid','')
#         if current_area:
#             area_object = Areas.objects.get(ar_id=current_area)
#             context['areaname'] = area_object.old_area_id
#         return context
#
#     def get_queryset(self):
#         current_area = self.request.GET.get('areaid','')
#         if current_area:
#             area_object=Areas.objects.get(ar_id=current_area)
#             object_list = area_object.nucacids_set.all().order_by('-nu_id')
#         else:
#             object_list = NucAcids.objects.all().order_by('-nu_id')[:100]
#
#         query = self.request.GET.get('q')
#         # object_list = NucAcids.objects.all().order_by('-nu_id')
#         if query:
#             object_list = NucAcids.objects.filter(
#             Q(na_type__icontains=query
#             ) |Q(method__icontains=query)
#             ).order_by('-nu_id')
#         # print(object_list)
#         return object_list
#
# class NucAcidUpdate(UpdateView):
#     model=NucAcids
#     template_name = 'libprep/nucacid_update_single.html'
#     form_class = NucAcidsForm
#     success_message = 'Nucleic Acid updated sucessfully'
#     success_url = reverse_lazy('nucacids-list')
#
#     # def save(self, commit=True):
#     #     instance = super(NucAcidsForm, self).save(commit=False)
#     #     instance.amount = self.cleaned_data['qubit'] * self.cleaned_data['volume']
#     #     if commit:
#     #         instance.save()
#     #     return instance
#
# class NucAcidDelete(DeleteView):
#     model = NucAcids
#     # form_class = PatientForm
#     template_name = 'libprep/nucacid_confirm_delete.html'
#     success_message = 'Nucleic Acid deleted sucessfully'
#     # fields = ['pat_id','sex','race','source','project','notes']
#     success_url = reverse_lazy('nucacids-list')
#
# def extract_nucacids(request):
#     form = ExtractNucleicAcids
#     selected_areas=request.session['selected_areas']
#     # The next for loop below generates area_list to be displayed in the form
#     area_list=[]
#     for area in selected_areas:
#         area_obj=Areas.objects.get(pk=area)
#         area_name=area_obj.old_area_id
#         area_block=area_obj.block.old_block_id
#         area_list.append(area_name+' from block: '+ area_block)
#     if request.method=='POST':
#         form = ExtractNucleicAcids(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             #now in the object cd, you have the form as a dictionary.
#             add_nucs_to_area(request, selected_areas, cd)
#             return redirect(reverse('areas-list'))
#     else:
#         form=form()
#         return render(request, 'libprep/extract_nucacids.html', context={'selected_areas':selected_areas, 'form': form, 'area_list': area_list})#to your redirect
#
# def edit_nucacids(request):
#     NucAcidsFormset = modelformset_factory(NucAcids,
#         formset = BaseNucAcids,
#         fields = ('nu_id', 'na_type', 'date_extr', 'method', 'qubit', 'volume', 'amount',
#                     're_ext', 'total_ext', 'na_sheared', 'shearing_vol', 'te_vol',),
#         # exclude=('area','old_na_id'),
#         widgets = {
#                     'na_type': TextInput(attrs={'size': '5'}),
#                     'nu_id': TextInput(attrs={'readonly': 'readonly', 'size': '5'}),
#                     'date_extr':DateInput(attrs={'size': '12'}),
#                     'method':DateInput(attrs={'size': '6'}),
#                     'qubit': TextInput(attrs={'size': '5'}),
#                     'volume': TextInput(attrs={'size': '5'}),
#                     'amount': TextInput(attrs={'size': '6'}),
#                     're_ext': TextInput(attrs={'size': '5'}),
#                     'total_ext': TextInput(attrs={'size': '7'}),
#                     'na_sheared': TextInput(attrs={'size': '5'}),
#                     'shearing_vol': TextInput(attrs={'size': '5'}),
#                     'te_vol': TextInput(attrs={'size': '6'}),
#             },
#         # formset = BaseNucAcidsFormSet,
#         can_delete=True,
#         extra=0,
#     )
#     # qset = NucAcids.objects.filter(NucAcids.objects.all().order_by('-nu_id')[:24])
#     # formset=NucAcidsFormset
#     helper = NucAcidsFormSetHelper()
#     # helper.template = 'bootstrap/table_inline_formset.html'
#     if request.method == 'POST':
#         #deal with posting the data
#         formset = NucAcidsFormset(request.POST)
#         print('Postrequest')
#         if formset.is_valid():
#             #if it is not valid then the "errors" will fall through and be returned
#             formset.save()
#         else:
#             print('NOT VALID')
#             print(formset.errors)
#     else:
#         formset = NucAcidsFormset()
#         print('NOPostrequest')
#         # print(formset)
#     return render(request, 'libprep/nucacids_update.html', {'formset': formset, 'helper':helper})#to your redirect


# class NucacidsUpdateView(CreateView):
#     # For adding nucacids to an area, or editing them.

#     model = NucAcids
#     template_name = 'libprep/nucacids-update'

#     def get(self, request, *args, **kwargs):
#         # The NA we're editing:
#         self.object = self.get_object(queryset=NucAcids.objects.all())
#         return super().get(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         # The NA we're uploading for:
#         self.object = self.get_object(queryset=NucAcids.objects.all())
#         print(self, request, args, kwargs)
#         return super().post(request, *args, **kwargs)

#     # def get_form(self, form_class=None):
#     #     # Use our big formset of formsets, and pass in the Areas object.
#     #     return AreasWithNucAcidsFormset(
#     #                         **self.get_form_kwargs(), instance=self.object)

#     def form_valid(self, form):
#         # If the form is valid, redirect to the success URL.
#         form.save()

#         messages.add_message(
#             self.request,
#             messages.SUCCESS,
#             'Changes were saved.'
#         )
#         return HttpResponseRedirect(self.get_success_url())

#     def get_success_url(self):
#         return reverse('nucacids-update', kwargs={'pk': self.object.pk})

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['query'] = self.request.GET.get('q')
#         return context
#         #return render(request, "patients-list", context)

# NucAcidsFormset=modelformset_factory(Nucacids,
#     form= NucacidsForm,
#     fields = ('nu_id', 'na_type', 'date_extr', 'method', 'qubit', 'volume', 'amount',
#                're_ext', 'total_ext', 'na_sheared', 'shearing_vol', 'te_vol', ),
#     labels = {'nu_id': _('NA-ID'),
#             'na_type': _('Type of NucAcid'),
#             'date_extr': _('Extraction Date'),
#             'method': _('Extraction Method'),
#             'qubit': _('Qubit'),
#             'volume': _('Volume'),
#             'amount': _('Total Amount [ng]'),
#             're_ext': _('Re-Extraction [ng]'),
#             'total_ext': _('Total Extracted [ng]'),
#             'na_sheared': _('NA Sheared [ng]'),
#             'shearing_vol': _('Shearing Vol [µl]'),
#             'te_vol': _('TE Vol [µl]')
#             },
#     extra=1,
#     can_delete=True
#     )

# class NucAcidsCreateView(CreateView):
#     model = Areas
#     fields = ["area_type",'old_block_id']

#     def get_context_data(self, **kwargs):
#         # we need to overwrite get_context_data
#         # to make sure that our formset is rendered
#         data = super().get_context_data(**kwargs)
#         if self.request.POST:
#             data["nucacids"] = NucAcidsFormset(self.request.POST)
#         else:
#             data["nucacids"] = NucAcidsFormset()
#         return data

#     def form_valid(self, form):
#         context = self.get_context_data()
#         nucacids = context["nucacids"]
#         self.object = form.save()
#         if nucacids.is_valid():
#             nucacids.instance = self.object
#             nucacids.save()
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse("areas-list")

# class AreasUpdateView(UpdateView):
#     model = Areas
#     fields = ["old_block_id",'area_type']
#     template_name = 'libprep/nucacids.html'
#     def get_context_data(self, **kwargs):
#         # we need to overwrite get_context_data
#         # to make sure that our formset is rendered.
#         # the difference with CreateView is that
#         # on this view we pass instance argument
#         # to the formset because we already have
#         # the instance created
#         data = super().get_context_data(**kwargs)
#         if self.request.POST:
#             data["nucacs"] = NucAcidsFormset(self.request.POST, instance=self.object)
#         else:
#             data["nucacs"] = NucAcidsFormset(instance=self.object)
#         print(data)
#         return data
#     def form_valid(self, form):
#         context = self.get_context_data()
#         nucacids = context["nucacids"]
#         self.object = form.save()
#         if nucacids.is_valid():
#             nucacids.instance = self.object
#             nucacids.save()
#         return super().form_valid(form)
#     def get_success_url(self):
#         return reverse("areas-list")
