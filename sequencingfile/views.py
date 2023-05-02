from django.shortcuts import render
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async
from .models import SequencingFile
from .serializers import SequencingFileSerializer
from django.http import JsonResponse

@permission_required("sequencingfile.view_sequencingfile",raise_exception=True)
def sequencingfiles(request):
    return render(request, "sequencingfile_list.html", locals())

@permission_required_for_async("sequencingfile.view_sequencingfile")
def filter_sequencingfiles(request):
    sequencingfiles = SequencingFile().query_by_args(request.user,**request.GET)
    serializer = SequencingFileSerializer(sequencingfiles['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = sequencingfiles['draw']
    result['recordsTotal'] = sequencingfiles['total']
    result['recordsFiltered'] = sequencingfiles['count']

    return JsonResponse(result)
