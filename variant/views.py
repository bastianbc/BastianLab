from django.shortcuts import render
from .forms import FilterForm
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async
from .models import *
from .serializers import *
from django.http import JsonResponse

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

def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        filename = file.name

        # Read the file into a DataFrame using streaming
        df = pd.read_csv(file, sep='\t')

        # Load data into the database
        load_data_to_db(df, filename)

        return redirect('success_url')  # Redirect to a success page or another view

    return render(request, 'upload.html')  # Render the upload form
