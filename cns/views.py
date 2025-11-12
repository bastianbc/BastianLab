from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from core.decorators import permission_required_for_async
from .serializers import CnsSerializer
from cns.models import Cns
from cns.forms import FilterForm
from django.http import JsonResponse


@permission_required("cns.view_cns",raise_exception=True)
def cns(request):
    filter = FilterForm()
    return render(request, "cns_list.html", locals())

@permission_required_for_async("cns.view_cns")
def filter_cns(request):
    cns = Cns().query_by_args(request.user,**request.GET)
    serializer = CnsSerializer(cns['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = cns['draw']
    result['recordsTotal'] = cns['total']
    result['recordsFiltered'] = cns['count']
    return JsonResponse(result)
