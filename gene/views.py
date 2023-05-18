from django.shortcuts import render
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async
from .models import *
from .serializers import *
from django.http import JsonResponse

def genes(request):
    return render(request,"genes.html",locals())

@permission_required_for_async("gene.view_gene")
def filter_genes(request):
    genes = Gene.query_by_args(request.user,**request.GET)
    serializer = GeneSerializer(genes['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = genes['draw']
    result['recordsTotal'] = genes['total']
    result['recordsFiltered'] = genes['count']

    return JsonResponse(result)
