from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required,permission_required
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from .serializers import BaitSerializer

@permission_required("bait.view_bait",raise_exception=True)
def baits(request):
    return render(request,"bait_list.html",locals())

@permission_required("bait.add_bait",raise_exception=True)
def new_bait(request):
    if request.method=="POST":
        form = BaitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Bait was created successfully")
            return redirect('/bait')
        else:
            messages.error(request,"Bait wasn't created!")
    else:
        form = BaitForm()
    return render(request,"bait.html",locals())

@permission_required("bait.change_bait",raise_exception=True)
def edit_bait(request,id):
    instance = Bait.objects.get(id=id)
    if request.method=="POST":
        form = BaitForm(request.POST,instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request,"Bait was updated successfully")
            return redirect('/bait')
        else:
            messages.error(request,"Bait wasn't updated!")
    else:
        form = BaitForm(instance=instance)
    return render(request,"bait.html",locals())

@permission_required("bait.delete_bait",raise_exception=True)
def delete_bait(request,id):
    try:
        instance = Bait.objects.get(id=id)
        instance.delete()
        messages.success(request, "Bait was deleted successfully")
        return redirect('/bait')
    except Exception as e:
        messages.error(request, "Bait wasn't deleted!")
    return redirect(coming_url)

@permission_required("bait.view_bait",raise_exception=True)
def filter_baits(request):
    baits = Bait().query_by_args(**request.GET)
    serializer = BaitSerializer(baits['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = baits['draw']
    result['recordsTotal'] = baits['total']
    result['recordsFiltered'] = baits['count']

    return JsonResponse(result)

@permission_required("bait.view_bait",raise_exception=True)
def get_bait_choices(request):
    serializer = BaitSerializer(Bait.objects.all(), many=True)
    return JsonResponse(serializer.data,safe=False)
