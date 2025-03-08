from django.shortcuts import render
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async
from .models import Cns
from django.http import JsonResponse

@permission_required("qc.view_qc",raise_exception=True)
def sample_qcs(request):
    filter = FilterForm()
    return render(request, "cns_list.html", locals())

@permission_required_for_async("qc.view_qc")
def filter_cns(request):
    cns = Cns().query_by_args(request.user,**request.GET)
    serializer = CnsSerializer(cns['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = cns['draw']
    result['recordsTotal'] = cns['total']
    result['recordsFiltered'] = cns['count']
    return JsonResponse(result)
