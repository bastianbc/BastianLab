import re
from django.forms.models import ModelForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.base import ContextMixin
from .models import Parts, Accessions
from .forms import AreaForm, AreaUpdateForm
from lab.models import Areas, Patients
from blocks.models import *
from projects.models import Projects
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from django.db.models import Q
from django.shortcuts import render
from django.contrib import messages

from django.utils.http import urlencode
from django.urls import reverse
from django import template

# register = template.Library()
# @register.simple_tag(takes_context=True)
# def url_replace(context, **kwargs):
#     # This is to allow GET parameters to be preserved in pagination
#     # https://stackoverflow.com/questions/2047622/how-to-paginate-django-with-other-get-variables
#     query = context['request'].GET.copy()
#     if query.get('page'): query.pop('page')
#     query.update(kwargs)
#     return query.urlencode()

def build_url(*args, **kwargs):
    """##This function builds a url for redirect, incorporating search parameters. """
    # This solved a difficult problem of returning
    # to the BlockList of the same project after e.g. deleting or updating a block
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urlencode(get)
    return url

def sorted_nicely(l):
    """ Sort the given iterable in the way that humans expect. Jeff Atwood"""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

class BlockDelete(DeleteView):
    model = Blocks
    template_name = 'accession/block_confirm_delete.html'
    template_name_suffix = '_confirm_delete'
    success_message = 'Block deleted sucessfully'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk=self.kwargs.get('pk')
        # Needs pk otherwise can't properly create url
        # projectid=self.request.GET.get('projectid')
        return locals()

    def get_success_url(self):
        projectid=self.request.GET.get('projectid','')
        patientid=self.request.GET.get('patientid','')
        if projectid:
            return build_url('block-list', get={'projectid': projectid})
        elif patientid:
            return build_url('block-list', get={'patientid': patientid})
        else: return reverse('block-list')



# class BlockUpdate(SuccessMessageMixin, UpdateView):
#     model = Blocks
#     form_class = BlockForm
#     template_name = 'accession/blocks_update_form.html'
#     success_message = 'Block updated sucessfully'
#
#
#     def get_success_url(self):
#         projectid=self.request.GET.get('projectid')
#         return build_url('block-list', get={'projectid': projectid})
#

class PartList(ListView):
    model = Parts
    template_name = 'accession/part_list.html'
    context_object_name = 'all_parts'
    paginate_by = 4



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        context['pk'] = self.kwargs['pk']
        proj_name=Projects.objects.get(pk=self.kwargs['pk'])
        context['proj_name'] = proj_name
        return context


    def get_queryset(self):
        query = self.request.GET.get('q')
        block_list=self.request.GET.getlist('blocks_selected')
        object_list = Parts.objects.all().order_by('block_id')[:4]
        proj_name=Projects.objects.get(pk=self.kwargs['pk'])
        if query:
            object_list = Parts.objects.filter(accession=query).order_by('block_id')
        if block_list:
            addparts(self.request, block_list,proj_name)
        return object_list

def is_valid_query(param):
    return param != '' and param is not None
    #     return(True)
    # else:
    #     return(False)

def make_block_id(block_in):
    ## This creates the format L19-1222A used in the Blocks table
    department=block_in.accession.dept_code
    path_nr=block_in.block_id
    return(department+path_nr)

def get_mm_data(block_in):
    ## This checks whether there is a matching entry in ip_melanomas and gets that data
    if hasattr(block_in.block_id,'Melanomas'):
    # if block_in.block_id.part:
        # There is an entry in Melanomas
        ulc=block_in.block_id.ulceration
        stage=block_in.block_id.p_stage
        thick=block_in.block_id.thickness
        mits=block_in.block_id.mitoses
        subtype=block_in.block_id.subtype

    else:
        ulc=stage=thick=mits=subtype=''
    return({'ulc': ulc,'stage': stage,'thick':thick,'mits':mits,'subtype':subtype})

def addparts(request, block_list, proj_name):
    blocks_to_add = block_list
    # associated_project=Projects.objects.get(name=request.POST.get('project'))
    if blocks_to_add:
            selected_blocks = Parts.objects.filter(block_id__in=blocks_to_add)
            # selected_blocks = Parts.objects.filter(block_id=blocks_to_add)
            for block in selected_blocks:
                block_out=make_block_id(block)
                mm_data=get_mm_data(block)
                does_exist = Blocks.objects.filter(old_block_id = block_out).exists()
                if does_exist:
                    messages.warning(request, 'Block '+block_out+' already exists in project  '
                                    + proj_name.name +'. No changes were made to database')
                else:
                    # new_patient=Patients(
                    #     pa_id=block.dept_number.pat_id.pat_id,
                    #     sex=block.dept_number.pat_id.gender,
                    #     race='U',
                    #     source='UCSF',
                    #     dob=block.dept_number.pat_id.birth_year
                    #     )
                    # new_patient.save(force_insert=True)
                    new_patient, patient_created = Patients.objects.update_or_create(
                        # pa_id=block.accession.patient.pat_id,
                        defaults={
                            'sex':block.accession.patient.gender,
                            'race':block.accession.patient.race,
                            'source':'UCSF',
                            'dob':block.accession.patient.birth_year,
                            'pat_id':'New'+block.accession.patient.pat_id
                            },
                        pa_id=block.accession.patient.pat_id
                        )

                    new_block, block_created = Blocks.objects.update_or_create(
                        defaults={
                            'body_site':block.site_text,
                            'ulceration':mm_data['ulc'],
                            'fixation':'FFPE',
                            'diagnosis':block.dx_text,
                            'storage':'DermPath',
                            'notes':block.note,
                            'age':block.accession.age,
                            'gross':block.gross,
                            'clinical':block.accession.clinical,
                            'micro':block.micro,
                            'site_code':block.site_code,
                            'icd9':block.icd9

                        },
                        project=proj_name,
                        # This passes the object itself rather than the key (which didn't work)
                        patient=new_patient,
                        old_block_id=block_out
                        )
                    messages.success(request, 'Block '+block_out+' added to project '
                                    + proj_name.name +' successfully')
            # context={'selected_areas':selected_areas}
        # return redirect('nucacids-update')
    return redirect('part-list')

class BlockList(ListView):
    # ""Lists the blocks for the current project""
    model = Blocks
    template_name = 'accession/block_list.html'
    context_object_name = 'all_blocks'
    paginate_by = 15

    def get_queryset(self):
        current_project=self.request.GET.get('projectid','')
        current_patient=self.request.GET.get('patientid','')
        # projectid and patientid get injected in the project- or patient-list template, respectively.
        # The information is needed to create the respective queryset and header (e.g. projectname)
        # for the BlockList view
        # The data needs to be preserved to remain available during pagination, and is stored in request.session
        if current_project:
            # current_project=int(self.kwargs.get('projectid'))
            project_object=Projects.objects.get(pr_id=current_project)
            all_blocks = project_object.blocks_set.all()
            # self.request.session['source'] = 'project'
            # self.request.session['source_obj_name'] = project_object.abbreviation
            # self.request.session['source_obj_id'] = project_object.pr_id
        elif current_patient:
            patient_object=Patients.objects.get(pa_id=current_patient)
            all_blocks = patient_object.blocks_set.all()
        else:
            all_blocks = Patients.objects.all()
        return all_blocks
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projectid=self.request.GET.get('projectid','')
        patientid=self.request.GET.get('patientid','')

        # source=self.request.session.get('source','')
        # current_patient=self.request.GET.get('patientid','')
        if projectid:
            # current_project=int(self.kwargs.get('projectid'))
            project_object=Projects.objects.get(pr_id=projectid)
            # object_list = project_object.blocks_set.all()
            context['projectname']=project_object.abbreviation
            # context['projectname']=self.request.session.get('source_obj_name','??')
        elif patientid:
            patient_object=Patients.objects.get(pa_id=patientid)
            # object_list = patient_object.blocks_set.all()
            context['patientname']=patient_object.pat_id

        # This is done to display the project abbreviation as a header of the list of blocks
        return context

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
