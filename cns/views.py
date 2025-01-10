from django.shortcuts import render
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async
from .serializers import CnsSerializer

@permission_required("cns.view_cns",raise_exception=True)
def cnses(request):
    return render(request, "cns_list.html", locals())

@permission_required_for_async("cns.view_cns")
def filter_cnses(request):
    cnses = Cns().query_by_args(request.user,**request.GET)
    serializer = CnsSerializer(cnses['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = cnses['draw']
    result['recordsTotal'] = cnses['total']
    result['recordsFiltered'] = cnses['count']

    return JsonResponse(result)
