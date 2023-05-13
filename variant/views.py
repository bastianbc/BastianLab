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

@permission_required_for_async("sequencingrun.view_sequencingrun")
def filter_variants(request):
    variants = VariantCall.query_by_args(request.user,**request.GET)
    serializer = VariantSerializer(variants['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = variants['draw']
    result['recordsTotal'] = variants['total']
    result['recordsFiltered'] = variants['count']

    return JsonResponse(result)
