from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required,permission_required
from .forms import *
from django.contrib import messages
from django.conf import settings
from .serializers import MethodSerializer
from django.http import JsonResponse

@permission_required("method.view_method",raise_exception=True)
def methods(request):
    return render(request,"method_list.html",locals())

@permission_required("method.add_method",raise_exception=True)
def new_method(request):
    if request.method=="POST":
        form = MethodForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Method created successfully")
            return redirect('/method')
        else:
            messages.error(request,"Method could not be created!")
    else:
        form = MethodForm()
    return render(request,"method.html",locals())

@permission_required("method.change_method",raise_exception=True)
def edit_method(request,id):
    instance = Method.objects.get(id=id)
    if request.method=="POST":
        form = MethodForm(request.POST,instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request,"Method updated successfully")
            return redirect('/method')
        else:
            messages.error(request,"Method could not be updated!")
    else:
        form = MethodForm(instance=instance)
    return render(request,"method.html",locals())

@permission_required("method.delete_method",raise_exception=True)
def delete_method(request,id):
    try:
        instance = Method.objects.get(id=id)
        instance.delete()
        messages.success(request, "Method deleted successfully")
    except Exception as e:
        messages.error(request, "Method could not be deleted!")
    
    return redirect('/method')

@permission_required("method.view_method",raise_exception=True)
def filter_methods(request):
    patients = Method().query_by_args(**request.GET)
    serializer = MethodSerializer(patients['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = patients['draw']
    result['recordsTotal'] = patients['total']
    result['recordsFiltered'] = patients['count']

    return JsonResponse(result)

def get_methods(request):
    serializer = MethodSerializer(Method.objects.all(), many=True)
    return JsonResponse(serializer.data, safe=False)
