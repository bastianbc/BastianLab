from django.shortcuts import render
from .forms import FilterForm
from core.decorators import permission_required_for_async
from .models import *
from .serializers import *
from django.http import JsonResponse
from .helper import variant_file_parser
from django.db import transaction
from django.conf import settings
import os
from django.db.models import Prefetch
from areas.models import Area
from blocks.models import Block
from blocks.variants_query import variant_queryset, VariantCustomSerializer
from .helper import get_kwarg_value

@permission_required_for_async("variant.view_variant")
def filter_variants(request):
    variants = VariantCall.query_by_args(request.user,**request.GET)
    kwargs = request.GET
    model_block = get_kwarg_value(kwargs, 'model_block')
    model_area = get_kwarg_value(kwargs, 'model_area')
    if model_block or model_area:
        serializer = VariantSerializerBlockArea(variants['items'], many=True)
    else:
        serializer = VariantSerializer(variants['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = variants['draw']
    result['recordsTotal'] = variants['total']
    result['recordsFiltered'] = variants['count']
    return JsonResponse(result)


def variants(request):
    filter = FilterForm()
    return render(request,"variants.html",locals())


def import_variants(request, name):
    """
    Import all variant files from a folder.
    If any file fails to process, all transactions are rolled back.
    """
    folder_path = os.path.join(settings.SEQUENCING_FILES_SOURCE_DIRECTORY, name)

    # Check if the folder exists
    if not os.path.exists(folder_path):
        return JsonResponse({
            "success": False,
            "message": "Couldn't find the folder you searched for"
        })

    # Get variant files in the folder
    files = os.listdir(folder_path)
    if not files:
        return JsonResponse({
            "success": False,
            "message": "No files found in the folder"
        })

    processing_stats = {
        "total_files": len(files),
        "processed_files": 0,
        "total_variants": 0,
        "successful_variants": 0,
        "errors": []
    }

    try:
        with transaction.atomic():
            # Process each file
            for filename in files:
                file_path = os.path.join(folder_path, filename)

                # Skip if not a file or not a .txt file
                if not os.path.isfile(file_path) or not filename.endswith('.txt'):
                    processing_stats["errors"].append(
                        f"Skipped {filename}: Not a valid text file"
                    )
                    continue

                # Parse and save data into the database
                success, message, stats = variant_file_parser(file_path, name)

                if not success:
                    # Raise exception to trigger rollback
                    raise Exception(f"Error processing {message}")

                # Update statistics
                processing_stats["processed_files"] += 1
                processing_stats["total_variants"] += stats["total_rows"]
                processing_stats["successful_variants"] += stats["successful"]

                # Add any errors from the file processing
                if stats.get("errors"):
                    processing_stats["errors"].extend([
                        f"{filename}: {error}" for error in stats["errors"]
                    ])

            # If any files had errors, raise exception to trigger rollback
            if processing_stats["errors"]:
                raise Exception("Some files had processing errors")

            return JsonResponse({
                "success": True,
                "message": "All files processed successfully",
                "statistics": {
                    "files_processed": processing_stats["processed_files"],
                    "total_variants_processed": processing_stats["successful_variants"],
                    "total_files": processing_stats["total_files"]
                }
            })

    except Exception as e:
        # All database changes will be rolled back
        return JsonResponse({
            "success": False,
            "message": str(e),
            "statistics": processing_stats,
            "errors": processing_stats["errors"]
        })

# def get_variants_by_area(request):
#     area_id = request.GET.get('area_id')
#     analysis_id = request.GET.get('analysis_id')
#
#     # DataTables parameters
#     draw = int(request.GET.get('draw', 1))
#     start = int(request.GET.get('start', 0))
#     length = int(request.GET.get('length', 10))
#     search_value = request.GET.get('search[value]', '')
#
#     # Sorting parameters
#     order_column_index = request.GET.get('order[0][column]', 0)
#     order_direction = request.GET.get('order[0][dir]', 'asc')
#
#     # Column names mapping
#     columns = ['sampleLibrary', 'gene', 'pVariant', 'coverage', 'vaf']
#     order_column = columns[int(order_column_index)]
#
#     # Base query
#     area = Area.objects.get(pk=area_id)
#     na_links = area.area_na_links.all()
#
#     # Get all sample libraries linked to these NAs
#     sample_libs = []
#     for na_link in na_links:
#         sample_libs.extend(na_link.nucacid.na_sl_links.all().values_list('sample_lib', flat=True))
#
#     # Initial queryset
#     variant_calls = VariantCall.objects.filter(
#         sample_lib__id__in=sample_libs
#     )
#
#     # Filter by analysis if provided
#     if analysis_id:
#         variant_calls = variant_calls.filter(analysis_run_id=analysis_id)
#
#     # Add prefetch related for optimization
#     variant_calls = variant_calls.prefetch_related(
#         'sample_lib',
#         Prefetch('g_variants', queryset=GVariant.objects.all()),
#         Prefetch('g_variants__c_variants', queryset=CVariant.objects.all()),
#         Prefetch('g_variants__c_variants__p_variants', queryset=PVariant.objects.all())
#     ).select_related('analysis_run')
#
#     # Get total records before filtering
#     total_records = variant_calls.count()
#
#     # Apply search if provided
#     if search_value:
#         variant_calls = variant_calls.filter(
#             Q(sample_lib__name__icontains=search_value) |
#             Q(g_variants__c_variants__gene__name__icontains=search_value) |
#             Q(g_variants__c_variants__p_variants__reference_residues__icontains=search_value)
#         )
#
#     # Get total records after filtering
#     total_filtered_records = variant_calls.count()
#
#     # Apply pagination
#     variant_calls = variant_calls[start:start + length]
#
#     # Prepare variants data
#     variants_data = []
#     for vc in variant_calls:
#         for g_variant in vc.g_variants.all():
#             for c_variant in g_variant.c_variants.all():
#                 variant_data = {
#                     'sampleLibrary': vc.sample_lib.name,
#                     'gene': c_variant.gene.name,
#                     'pVariant': (
#                         (c_variant.p_variants.first().reference_residues or '') +
#                         str(c_variant.p_variants.first().start or '') +
#                         (c_variant.p_variants.first().inserted_residues or '')
#                     ) if c_variant.p_variants.first() else '',
#                     'coverage': vc.coverage,
#                     'vaf': round((vc.alt_read / (vc.ref_read + vc.alt_read)) * 100, 2) if (vc.ref_read + vc.alt_read) > 0 else 0,
#                 }
#                 variants_data.append(variant_data)
#
#     # Check if this is the initial request (no draw parameter)
#     if not 'draw' in request.GET:
#         # Prepare area and analysis information
#         analyses = VariantCall.objects.filter(
#             sample_lib__id__in=sample_libs
#         ).select_related('analysis_run').distinct('analysis_run').values(
#             'analysis_run_id', 'analysis_run__name'
#         )
#
#         response_data = {
#             'area': {
#                 'id': area.id,
#                 'name': area.name,
#                 'he_image': area.image.url if area.image else None,
#                 'block': {
#                     'name': area.block.name if area.block else '',
#                     'body_site': area.block.body_site.name if area.block and area.block.body_site else '',
#                     'diagnosis': area.block.diagnosis.name if area.block and area.block.diagnosis else ''
#                 }
#             },
#             'analyses': [
#                 {
#                     'analysis_id': analysis['analysis_run_id'],
#                     'analysis_name': analysis['analysis_run__name']
#                 }
#                 for analysis in analyses
#             ]
#         }
#         return JsonResponse(response_data)
#
#     # Return DataTables formatted response
#     return JsonResponse({
#         'draw': draw,
#         'recordsTotal': total_records,
#         'recordsFiltered': total_filtered_records,
#         'data': variants_data
#     })


# def get_variants_by_block(request):
#     block_id = request.GET.get('block_id')
#     analysis_id = request.GET.get('analysis_id')
#     # DataTables parametreleri
#     draw = int(request.GET.get('draw', 1))
#     start = int(request.GET.get('start', 0))
#     length = int(request.GET.get('length', 10))
#     search_value = request.GET.get('search[value]', '')
#
#     # Sıralama parametreleri
#     order_column_index = request.GET.get('order[0][column]', 0)
#     order_direction = request.GET.get('order[0][dir]', 'asc')
#
#     # Column names mapping
#     columns = ["id", "areas", "sample_lib", "genes", "DT_RowId", "coverage", "vaf"]
#     order_column = columns[int(order_column_index)]
#     # Base query
#     block = Block.objects.get(pk=block_id)
#
#     variant_calls = variant_queryset(block)
#
#     total_records = variant_calls.count()
#
#     # Apply search if provided
#     if search_value:
#         variant_calls = variant_calls.filter(
#             Q(sample_lib__name__icontains=search_value) |
#             Q(g_variants__c_variants__gene__name__icontains=search_value) |
#             Q(g_variants__c_variants__p_variants__reference_residues__icontains=search_value)
#         )
#
#     # Get total records after filtering
#     total_filtered_records = variant_calls.count()
#
#     # Apply pagination
#     variant_calls = variant_calls.order_by(order_column)[start:start + length]
#
#     serializer = VariantCustomSerializer(variant_calls, many=True)
#     result = dict()
#     result['data'] = serializer.data
#     result['draw'] = draw
#     result['recordsTotal'] = total_records
#     result['recordsFiltered'] = total_filtered_records
#
#     return JsonResponse(result)

def get_variants_by_area(request):
    # get request parameters
    area_id = request.GET.get('area_id')

    # datatables parameters
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')

    # ordering parameters
    order_column_index = request.GET.get('order[0][column]', 0)
    order_direction = request.GET.get('order[0][dir]', 'asc')

    # colmun name mapping
    columns = ["analysis_run_id", "analysis_run_name", "gene_name", "samplelib_name", "p_variant", "alias", "coverage", "vaf"]

    # set to order column
    order_column = columns[int(order_column_index)]

    # set to order direction
    if order_direction == 'desc':
        order_column = f"-{order_column}"

    # main query
    variants = VariantsView.objects.filter(area_id=area_id)

    total_records = variants.count()

    # search parameters
    if search_value:
        variants = variants.filter(
            Q(area_name__icontains=search_value) |
            Q(samplelib_name__icontains=search_value) |
            Q(gene_name__icontains=search_value) |
            Q(c_var__icontains=search_value) |
            Q(g_ref__icontains=search_value) |
            Q(g_alt__icontains=search_value) |
            Q(func__icontains=search_value)
        )

    # result count after the query
    total_filtered_records = variants.count()

    # apply pagination
    variants = variants.order_by(order_column)[start:start + length]

    # convert to data format of datatables
    data = []
    for variant in variants:
        data.append({
            'DT_RowId': f"variant_{variant.variantcall_id}",
            'variantcall_id': variant.variantcall_id,
            'analysis_run_name': variant.analysis_run_name,
            'gene_name': variant.gene_name,
            'samplelib_name': variant.samplelib_name,
            'p_variant': variant.reference_residues if variant.reference_residues else '',
            'alias': variant.alias if variant.alias else '',
            'coverage': variant.coverage,
            'vaf': round(variant.vaf, 2) if variant.vaf else 0,
        })

    result = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': total_filtered_records,
        'data': data
    }

    return JsonResponse(result)
