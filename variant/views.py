from django.shortcuts import render
from .forms import FilterForm
from core.decorators import permission_required_for_async
from .models import *
from .serializers import *
from django.http import JsonResponse
from django.db import transaction
from django.conf import settings
import os
from django.db.models import Prefetch
from django.http import HttpResponse
from .walk_sequencing_data import create_file_tree

@permission_required_for_async("variant.view_variant")
def filter_variants(request):
    variants = VariantsView.query_by_args(request.user,**request.GET)
    data = []
    for variant in variants['items']:
        data.append({
            'id': variant.gvariant_id,
            'chrom': variant.chromosome,
            'start': variant.g_start,
            'ref': variant.ref_read,
            'alt': variant.alt_read,
            'areas': variant.area_name,
            'blocks': variant.block_name,
            'sample_libs': variant.samplelib_name,
            'genes': variant.gene_name,
            'cosmic_gene_symbol': variant.cosmic_gene_symbol,
            'cosmic_aa': variant.cosmic_aa,
            'cosmic_primary_site_counts': variant.cosmic_primary_site_counts,
            'total_calls': variant.total_site_counts,
        })

    result = {
        'draw': int(request.GET.get('draw', 1)),
        'recordsTotal': variants['total'],
        'recordsFiltered': variants['count'],
        'data': data
    }
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
                return JsonResponse({
                    "success": False,
                    "message": "Some files had processing errors",
                    "statistics": {
                        "files_processed": processing_stats["processed_files"],
                        "total_variants_processed": processing_stats["successful_variants"],
                        "total_files": processing_stats["total_files"]
                    }
                })

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
    columns = ["analysis_run_id", "analysis_run_name", "gene_name", "variant",
               "alias", "coverage", "vaf", "caller", "cosmic_gene_symbol", "cosmic_aa", "total_site_counts"]

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
            # 'DT_RowId': f"variant_{variant.variantcall_id}",
            'gvariant_id': variant.gvariant_id,
            'analysis_run_name': variant.analysis_run_name,
            'gene_name': variant.gene_name,
            'p_variant': variant.variant if variant.variant else '',
            'alias': variant.alias if variant.alias else '',
            'coverage': variant.coverage,
            'vaf': round(variant.vaf, 2) if variant.vaf else 0,
            'caller': variant.caller,
            'cosmic_gene_symbol': variant.cosmic_gene_symbol,
            'cosmic_aa': variant.cosmic_aa,
            'total_site_counts': variant.total_site_counts,
            'cosmic_primary_site_counts': variant.cosmic_primary_site_counts,
        })

    result = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': total_filtered_records,
        'data': data
    }

    return JsonResponse(result)

