from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required,permission_required
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from .serializers import BodySerializer

@permission_required("body.view_body",raise_exception=True)
def bodys(request):
    return render(request,"body_list.html",locals())

@permission_required("body.add_body",raise_exception=True)
def new_body(request):
    if request.method=="POST":
        form = BodyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Body was created successfully")
            return redirect('/body')
        else:
            messages.error(request,"Body wasn't created!")
    else:
        form = BodyForm()
    return render(request,"body.html",locals())

@permission_required("body.change_body",raise_exception=True)
def edit_body(request,id):
    instance = Body.objects.get(id=id)
    if request.method=="POST":
        form = BodyForm(request.POST,instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request,"Body was updated successfully")
            return redirect('/body')
        else:
            messages.error(request,"Body wasn't updated!")
    else:
        form = BodyForm(instance=instance)
    return render(request,"body.html",locals())

@permission_required("body.delete_body",raise_exception=True)
def delete_body(request,id):
    try:
        instance = Body.objects.get(id=id)
        instance.delete()
        messages.success(request, "Body was deleted successfully")
        return redirect('/body')
    except Exception as e:
        messages.error(request, "Body wasn't deleted!")
    return redirect(coming_url)

@permission_required("body.view_body",raise_exception=True)
def filter_bodys(request):
    bodys = Body().query_by_args(**request.GET)
    serializer = BodySerializer(bodys['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = bodys['draw']
    result['recordsTotal'] = bodys['total']
    result['recordsFiltered'] = bodys['count']

    return JsonResponse(result)

@permission_required("body.view_body",raise_exception=True)
def get_body_choices(request):
    serializer = BodySerializer(Body.objects.all(), many=True)
    return JsonResponse(serializer.data,safe=False)
