from django.shortcuts import render
from .forms import FilterForm
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async
from .models import *
from .serializers import *
from django.http import JsonResponse
from .helper import variant_file_parser

def variants(request):
    filter = FilterForm()
    return render(request,"variants.html",locals())

@permission_required_for_async("variant.view_variant")
def filter_variants(request):
    variants = VariantCall.query_by_args(request.user,**request.GET)
    serializer = VariantSerializer(variants['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = variants['draw']
    result['recordsTotal'] = variants['total']
    result['recordsFiltered'] = variants['count']

    return JsonResponse(result)

def import_variants(request, name):
    import os
    from django.conf import settings
    from .helper import variant_file_parser

    folder_path = os.path.join(settings.SMB_DIRECTORY, name)

    # Check if the folder exists
    if os.path.exists(folder_path):
        # Get variant files in the folder
        files = os.listdir(folder_path)

        for filename in files:
            # parsing and saving data into the database
            file_path = os.path.join(folder_path, filename)
            variant_file_parser(file_path, name)

        return JsonResponse({"success": True, "message": "Files processed successfully"})

    else:
        return JsonResponse({"success": False, "message": "Couldn't find the folder you searched for"})
