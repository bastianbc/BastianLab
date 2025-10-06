import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async
from .models import SampleQC
from .forms import SampleQCForm
from django.http import JsonResponse
from qc.serializers import SampleQCSerializer
import logging
import os
from django.http import FileResponse, HttpResponse
from django.conf import settings

logger = logging.getLogger("file")


@permission_required("qc.view_sampleqc",raise_exception=True)
def sample_qcs(request):
    filter = SampleQCForm()
    return render(request, "qc_list.html", locals())

@permission_required_for_async("qc.view_sampleqc")
def filter_sampleqcs(request):
    qc = SampleQC().query_by_args(request.user,**request.GET)
    serializer = SampleQCSerializer(qc['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = qc['draw']
    result['recordsTotal'] = qc['total']
    result['recordsFiltered'] = qc['count']
    return JsonResponse(result)

@permission_required_for_async("qc.add_sampleqc")
def process_qc_metrics(request, ar_name):
    """
    Process QC metrics for a specific analysis run (identified by name) and return the summary report.
    """
    # Get analysis run name from URL parameter or request body
    if ar_name is None:
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                ar_name = data.get('ar_name')
            except json.JSONDecodeError:
                return JsonResponse(
                    {'error': 'Invalid JSON in request body'},
                    status=400
                )
        else:
            ar_name = request.GET.get('ar_name')

    # Validate analysis run name
    if not ar_name:
        return JsonResponse(
            {'error': 'Analysis run name is required'},
            status=400
        )

    # Process QC metrics for the analysis run
    try:
        logger.info(f"Processing QC metrics for analysis run '{ar_name}'")
        result = SampleQC.process_and_save_from_analysis_run(ar_name)
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Error processing QC metrics for run '{ar_name}': {str(e)}")
        return JsonResponse(
            {'error': f'Internal server error: {str(e)}'},
            status=500
        )

@permission_required("qc.view_sampleqc",raise_exception=True)
def get_sampleqc_detail(request, pk):
    sample_qc = get_object_or_404(SampleQC, pk=pk)
    form = SampleQCForm(instance=sample_qc)
    return render(request, 'qc.html', {
        'sample_qc': sample_qc,
        'form': form,
    })


def serve_pdf(request, pk):
    # Convert the relative path to an absolute path in your filesystem
    qc = SampleQC.objects.get(pk=pk)
    file_path = os.path.join(qc.variant_file.directory, qc.insert_size_histogram)
    print("### file path: ", file_path)
    try:
        # Serve the file
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        return HttpResponse("PDF not found", status=404)
