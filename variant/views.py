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

    analysis_run = AnalysisRun.objects.get(id=id)

    folder_path = os.path.join(settings.SMB_DIRECTORY, analysis_run.name)

    # Check if the folder exists
    if os.path.exists(folder_path):
        # Get variant files in the folder
        files = os.listdir(folder_path)

        for file_name in files:
            # parsing and saving data into the database
            variant_file_parser(file)

        # Return a success response
        return JsonResponse({"success": True, "message": "Files processed successfully"})

    else:
        # Return an error response if the folder doesn't exist
        return JsonResponse({"success": False, "message": "Couldn't find the folder you searched for"})
