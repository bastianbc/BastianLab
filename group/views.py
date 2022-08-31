from django.shortcuts import render,redirect
from .models import Group
from django.contrib.auth.decorators import login_required,permission_required
from .forms import GroupForm
from django.contrib import messages

@permission_required("view_group",raise_exception=True)
def groups(request):
    return render(request,"group_list.html",locals())

@permission_required("add_group",raise_exception=True)
def new_group(request):
    if request.method=="POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Group was created successfully")
            return redirect('/group')
        else:
            messages.error(request,"Group wasn't created!")
    else:
        form = GroupForm()
    return render(request,"group.html",locals())

@permission_required("change_group",raise_exception=True)
def edit_group(request,id):
    instance = Group.objects.get(id=id)
    if request.method=="POST":
        form = GroupForm(request.POST,instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request,"Group was updated successfully")
            return redirect('/group')
        else:
            messages.error(request,"Group wasn't updated!")
    else:
        form = GroupForm(instance=instance)
    return render(request,"group.html",locals())

@permission_required("delete_group",raise_exception=True)
def delete_group(request,id):
    try:
        instance = Group.objects.get(id=id)
        instance.delete()
        messages.success(request, "Group was deleted successfully")
        return redirect('/group')
    except Exception as e:
        messages.error(request, "Group wasn't deleted!")
    return redirect("/group")

def filter_groups(request):
    from .serializers import GroupSerializer
    from django.http import JsonResponse

    patients = Group().query_by_args(**request.GET)
    serializer = GroupSerializer(patients['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = patients['draw']
    result['recordsTotal'] = patients['total']
    result['recordsFiltered'] = patients['count']

    return JsonResponse(result)
