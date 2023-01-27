from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required,permission_required
from .forms import *
from django.contrib import messages
from .serializers import *
from django.http import JsonResponse
from core.decorators import permission_required_for_async

@permission_required("barcodeset.view_barcodeset",raise_exception=True)
def barcodesets(request):
    return render(request,"barcodeset_list.html",locals())

@permission_required("barcodeset.add_barcodeset",raise_exception=True)
def new_barcodeset(request):
    import csv
    from io import StringIO

    if request.method=="POST":
        form = NewBarcodesetForm(request.POST, request.FILES)

        if form.is_valid():
            barcode_set = form.save()

            file = form.cleaned_data["file"].read().decode('utf-8')

            reader = csv.reader(StringIO(file))

            for row in reader:
                try:
                    Barcode.objects.create(
                        barcode_set=barcode_set,
                        name=row[0],
                        i5=row[1],
                        i7=row[2]
                    )
                except Exception as e:
                    print(str(e))
                    pass

            messages.success(request,"Barcode set was created successfully")

            return redirect('/barcodeset')
        else:
            messages.error(request,"Barcode set wasn't created!")
    else:
        form = NewBarcodesetForm()
    return render(request,"barcodeset.html",locals())

@permission_required("barcodeset.change_barcodeset",raise_exception=True)
def edit_barcodeset(request,id):
    instance = Barcodeset.objects.get(id=id)
    if request.method=="POST":
        form = EditBarcodesetForm(request.POST,instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request,"Barcode set was updated successfully")
            return redirect('/barcodeset')
        else:
            messages.error(request,"Barcodeset wasn't updated!")
    else:
        form = EditBarcodesetForm(instance=instance)
    return render(request,"barcodeset.html",locals())

@permission_required("barcodeset.delete_barcodeset",raise_exception=True)
def delete_barcodeset(request,id):
    try:
        instance = Barcodeset.objects.get(id=id)
        instance.delete()
        messages.success(request, "Barcode set was deleted successfully")
    except Exception as e:
        messages.error(request, "Barcode set wasn't deleted! \n%s" % str(e))

    return redirect('/barcodeset')

@permission_required("barcodeset.view_barcodeset",raise_exception=True)
def filter_barcodesets(request):
    barcodesets = Barcodeset().query_by_args(**request.GET)
    serializer = BarcodesetSerializer(barcodesets['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = barcodesets['draw']
    result['recordsTotal'] = barcodesets['total']
    result['recordsFiltered'] = barcodesets['count']

    return JsonResponse(result)

@permission_required("barcodeset.view_barcode",raise_exception=True)
def barcodes(request,id):
    barcode_set = Barcodeset.objects.get(id=id)
    return render(request,"barcode_list.html",locals())

@permission_required("barcodeset.view_barcode",raise_exception=True)
def filter_barcodes(request):
    barcodes = Barcode().query_by_args(**request.GET)
    serializer = BarcodeSerializer(barcodes['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = barcodes['draw']
    result['recordsTotal'] = barcodes['total']
    result['recordsFiltered'] = barcodes['count']

    return JsonResponse(result)

@permission_required_for_async("capturedlib.change_capturedlib")
def edit_barcode_async(request):
    import re
    from core.utils import custom_update

    parameters = {}

    try:
        for k,v in request.POST.items():
            if k.startswith('data'):
                r = re.match(r"data\[(\d+)\]\[(\w+)\]", k)
                if r:
                    parameters["pk"] = r.groups()[0]
                    if v == '':
                        v = None
                    parameters[r.groups()[1]] = v

        custom_update(Barcode,pk=parameters["pk"],parameters=parameters)
    except Exception as e:
        print("%s in %s" % (str(e),__file__))
        return JsonResponse({"success":False})

    return JsonResponse({"success":True})

@permission_required("barcodeset.change_barcodeset",raise_exception=True)
def activate(request,id):
    barcode_set = Barcodeset.objects.get(id=id)
    barcode_set.activate()
    return render(request,"barcodeset_list.html",locals())
