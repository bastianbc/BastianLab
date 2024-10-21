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

def import_variants(request):
    import os
    from django.conf import settings
    from .helper import variant_file_parser
    name = 'SGLP-0774'
    folder_path = os.path.join(settings.SEQUENCING_FILES_SOURCE_DIRECTORY, name)
    print("&" * 30, folder_path)
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Get variant files in the folder
        files = os.listdir(folder_path)
        analysisrun_name = [file_name for file_name in files if "analysis_sheet" in file_name]
        print("&"*30, analysisrun_name)
        for filename in files:
            # parsing and saving data into the database
            file_path = os.path.join(folder_path, filename)
            if ".txt" in filename:
                print(filename)
                variant_file_parser(file_path, analysisrun_name[0])

        return JsonResponse({"success": True, "message": "Files processed successfully"})

    else:
        return JsonResponse({"success": True, "message": "Files processed successfully"})
        # return JsonResponse({"success": False, "message": "Couldn't find the folder you searched for"})
