from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from .models import *
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import *
from django.http import JsonResponse
import json
from django.contrib import messages
from blocks.models import *

def filter_areas(request):
    from .serializers import AreasSerializer

    areas = Areas().query_by_args(**request.GET)
    serializer = AreasSerializer(areas['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = areas['draw']
    result['recordsTotal'] = areas['total']
    result['recordsFiltered'] = areas['count']

    return JsonResponse(result)

def areas(request):
    return render(request,"area_list.html")

def new_area(request):
    if request.method=="POST":
        form = AreaForm(request.POST)
        if form.is_valid():
            area = form.save()
            messages.success(request,"Area %s was created successfully." % area.ar_id)
            return redirect("areas")
        else:
            messages.error(request,"Area wasn't created.")
    else:
        form = AreaForm()

    return render(request,"area.html",locals())

def new_area_async(request):
    selected_ids = json.loads(request.GET.get("selected_ids"))

    for id in selected_ids:
        block = Blocks.objects.get(bl_id=id)

        Areas.objects.create(block=block)

        return JsonResponse({"success":True})

    return JsonResponse({"success":False})

def edit_area(request,id):
    area = Areas.objects.get(ar_id=id)

    if request.method=="POST":
        form = AreaForm(request.POST,instance=area)
        if form.is_valid():
            area = form.save()
            messages.success(request,"Area %s was updated successfully." % area.ar_id)
            return redirect("areas")
        else:
            messages.error(request,"Area wasn't updated!")
    else:
        form = AreaForm(instance=area)

    return render(request,"area.html",locals())

def edit_area_async(request):
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

    custom_update(Areas,pk=parameters["pk"],parameters=parameters)

    return JsonResponse({"result":True})

def delete_area(request,id):
    try:
        area = Areas.objects.get(ar_id=id)
        area.delete()
        messages.success(request,"Area %s was deleted successfully." % area.ar_id)
        deleted = True
    except Exception as e:
        messages.error(request, "Area %s wasn't deleted!" % area.ar_id)
        deleted = False

    return JsonResponse({ "deleted":True })

class AreaList(ListView):
    # table_class = SimpleTable
    queryset = Areas.objects.all().order_by('-completion_date')
    template_name = 'libprep/areas_list.html'
    context_object_name = 'all_areas'

    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        current_block = self.request.GET.get('blockid','')
        if current_block:
            block_object=Blocks.objects.get(bl_id=current_block)
            context['blockname'] =block_object.old_block_id
        return context

    def get_queryset(self):
        current_block = self.request.GET.get('blockid','')
        if current_block:
            block_object=Blocks.objects.get(bl_id=current_block)
            object_list = block_object.areas_set.all().order_by('-ar_id')
        else:
            object_list = Areas.objects.all().order_by('-ar_id')
        query = self.request.GET.get('q')
        if query:
            object_list = Areas.objects.filter(
            Q(area_type__icontains=query
            ) |Q(block__project__abbreviation__icontains=query) |Q(block__old_block_id__icontains=query)
            ).order_by('-ar_id')
        return object_list



    def dispatch(self, request, *args, **kwargs):
        # the dispatch method injects the selected_areas
        # into request.session so that it remains accessible after the redirect. It gets removed after
        # add_nucs_to_area has run

        selected_areas = self.request.GET.getlist('areas_selected')
        if selected_areas:
            prior_selection = self.request.session.getlist('selected_areas','')
            request.session['selected_areas'] = prior_selection+selected_areas
            return HttpResponseRedirect(reverse('extract_nucacids'))
        else:
            return super().dispatch(request, *args, **kwargs)

class AreaCreate(CreateView, SuccessMessageMixin):
    model = Areas
    form_class = AreaForm
    template_name = 'accession/add_areas.html'
    success_message = success_message = "Area %(old_area_id)s was created successfully"
    def get_form_kwargs(self):
        """" This is required to get the initial values for old_area_id into the unbound form
        the project abbreviation gets added to the kwargs and then gets popped out again in the __init__ method
        of the form and provided as an initial value to the field old_area_id """
        kwargs = super(AreaCreate, self).get_form_kwargs()
        blockobject = Blocks.objects.get(bl_id=self.kwargs.get('pk'))
        # The following code is to determine the latest/highest old_area_id entry for the initial value for
        # the AreaForm
        projectabb = blockobject.project.abbreviation
        # project_areas = Areas.objects.filter(old_area_id__startswith=projectabb)
        project_areas = Areas.objects.filter(block__project__abbreviation__startswith=projectabb).values_list('old_area_id', flat=True)
        # print(project_areas)
        if project_areas:
            last_area = sorted_nicely(project_areas)[-1]
            digits=re.findall(r'\d+', last_area)
            # Gets a list of the numbers out of the last_area
            next_area_id = int(digits[-1])+1
            # Takes the last number from that list and adds 1
        else:
            # This is the first area for this project
            next_area_id = 1
        kwargs.update({'next_old_area_id': projectabb+'-'+str(next_area_id)})
        # Injects initial value for old_area_id
        return kwargs

    def get_success_url(self):
        projectid=self.request.GET.get('projectid')
        patientid=self.request.GET.get('patientid')
        if projectid:
            return build_url('block-list', get={'projectid': projectid})
        elif patientid:
            return build_url('block-list', get={'patientid': patientid})
        else:
            return build_url('block-list')



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk']=self.kwargs.get('pk')
        # Needs pk otherwise can't properly create url
        context['projectid']=self.request.GET.get('projectid')
        blockobject=Blocks.objects.get(bl_id=self.kwargs.get('pk'))
        context['projectabb'] = blockobject.project.abbreviation
        context['blockid']=blockobject.old_block_id
        context['dx'] = blockobject.diagnosis
        # print (type(kwargs))
        # kwargs['projectname']=kwargs['b']
        return context
        # return super().get_context_data(**kwargs)
    def form_valid(self, form):
        pk = self.kwargs.get('pk')
        form.instance.block = Blocks.objects.get(bl_id=pk)
        # form.instance.old_block_id = form.instance.block
        # Need to pass instance not the pk.
        return super(AreaCreate, self).form_valid(form)

class AreaUpdate(SuccessMessageMixin, UpdateView):
    slug_field= 'block_id'
    slug_url_kwarg = 'block_id'
    model = Areas
    form_class = AreaUpdateForm
    template_name = 'accession/area_update_form.html'
    success_message = 'Area updated sucessfully'
    def get_form_kwargs(self):
        """" This is required to get the initial values for investigator to the form to be updated
        Without this the MultiChoiceSelect isn't working"""
        kwargs = super().get_form_kwargs()
        investigator_default = Areas.objects.get(ar_id=self.kwargs.get('pk')).investigator
        kwargs.update({'investigator_default': investigator_default})
        # Injects initial value for old_area_id
        return kwargs
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['pk']=self.kwargs.get('pk')
    #     # Needs pk otherwise can't properly create url
    #     context['projectid']=self.request.GET.get('projectid')
    #     a=self.instance
    #     context['blockobject']=Areas.objects.get(ar_id=pk).block
        # context['projectabb'] = Areas.block.project.abbreviation
        # context['blockid']=Areas.block.old_block_id
        # context['dx'] = Areas.block.diagnosis
        # print (type(kwargs))
        # kwargs['projectname']=kwargs['b']
        # return context

    def get_success_url(self):
        if self.request.GET.get('projectid'):
            projectid=self.request.GET.get('projectid')
            return build_url('areas-list', get={'projectid': projectid})
        else:
            return build_url('areas-list')
    def form_valid(self, form):
        pk = self.kwargs.get('pk')
        block = Areas.objects.get(ar_id=pk).block.bl_id
        form.instance.block = Blocks.objects.get(bl_id=block)
        # This is required to preserve the relationship of the Areas object to Blocks
        return super().form_valid(form)

class AreaDelete(DeleteView):
    model = Areas
    template_name = 'accession/area_confirm_delete.html'
    template_name_suffix = '_confirm_delete'
    success_message = 'Area deleted sucessfully'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk=self.kwargs.get('pk')
        # Needs pk otherwise can't properly create url
        projectid=self.request.GET.get('projectid')
        return locals()

    def get_success_url(self):
        projectid=self.request.GET.get('projectid')
        return build_url('areas-list', get={'projectid': projectid})
