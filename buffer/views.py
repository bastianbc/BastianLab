from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required,permission_required
from .forms import *
from django.contrib import messages
from .serializers import BufferSerializer
from django.http import JsonResponse

@permission_required("buffer.view_buffer",raise_exception=True)
def buffers(request):
    return render(request,"buffer_list.html",locals())

@permission_required("buffer.add_buffer",raise_exception=True)
def new_buffer(request):
    if request.method=="POST":
        form = BufferForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Buffer was created successfully")
            return redirect('/buffer')
        else:
            messages.error(request,"Buffer wasn't created!")
    else:
        form = BufferForm()
    return render(request,"buffer.html",locals())

@permission_required("buffer.change_buffer",raise_exception=True)
def edit_buffer(request,id):
    instance = Buffer.objects.get(id=id)
    if request.method=="POST":
        form = BufferForm(request.POST,instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request,"Buffer was updated successfully")
            return redirect('/buffer')
        else:
            messages.error(request,"Buffer wasn't updated!")
    else:
        form = BufferForm(instance=instance)
    return render(request,"buffer.html",locals())

@permission_required("buffer.delete_buffer",raise_exception=True)
def delete_buffer(request,id):
    try:
        instance = Buffer.objects.get(id=id)
        instance.delete()
        messages.success(request, "Buffer was deleted successfully")
        return redirect('/buffer')
    except Exception as e:
        messages.error(request, "Buffer wasn't deleted!")
    return redirect(coming_url)

@permission_required("buffer.view_buffer",raise_exception=True)
def filter_buffers(request):
    from .serializers import BufferSerializer
    from django.http import JsonResponse

    buffers = Buffer().query_by_args(**request.GET)
    serializer = BufferSerializer(buffers['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = buffers['draw']
    result['recordsTotal'] = buffers['total']
    result['recordsFiltered'] = buffers['count']

    return JsonResponse(result)

@permission_required("bait.view_bait",raise_exception=True)
def get_buffer_choices(request):
    serializer = BufferSerializer(Buffer.objects.all(), many=True)
    return JsonResponse(serializer.data,safe=False)
