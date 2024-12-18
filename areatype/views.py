from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib import messages
from .serializers import AreaTypeSerializer
from django.http import JsonResponse
from .forms import *


@permission_required("areatype.view_areatype",raise_exception=True)
def areatypes(request):
    return render(request,"areatype_list.html",locals())


@permission_required("areatype.add_areatype",raise_exception=True)
def new_areatype(request):
    if request.method=="POST":
        form = AreaTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Area Type created successfully")
            return redirect('/areatype')
        else:
            messages.error(request,"Area Type could not be created!")
    else:
        form = AreaTypeForm()
    return render(request,"areatype.html",locals())

@permission_required("areatype.change_areatype",raise_exception=True)
def edit_areatype(request,id):
    instance = AreaType.objects.get(id=id)
    if request.method=="POST":
        form = AreaTypeForm(request.POST,instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request,"Area Type updated successfully")
            return redirect('/areatype')
        else:
            messages.error(request,"Area Type could not be updated!")
    else:
        form = AreaTypeForm(instance=instance)
    return render(request,"areatype.html",locals())

@permission_required("areatype.delete_areatype",raise_exception=True)
def delete_areatype(request,id):
    try:
        instance = AreaType.objects.get(id=id)
        instance.delete()
        messages.success(request, "Area Type deleted successfully")
    except Exception as e:
        messages.error(request, "Area Type could not be deleted!")

    return redirect('/areatype')

@permission_required("areatype.view_areatype",raise_exception=True)
def filter_areatype(request):

    areatypes = AreaType().query_by_args(**request.GET)
    serializer = AreaTypeSerializer(areatypes['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = areatypes['draw']
    result['recordsTotal'] = areatypes['total']
    result['recordsFiltered'] = areatypes['count']

    return JsonResponse(result)

@permission_required("areatype.view_areatype",raise_exception=True)
def get_area_type_choices(request):
    serializer = AreaTypeSerializer(AreaType.objects.all(), many=True)
    return JsonResponse(serializer.data,safe=False)
