from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async
from .serializers import CnsSerializer
from cns.models import Cns
from cns.forms import FilterForm
from django.http import JsonResponse

@permission_required("cns.view_cns",raise_exception=True)
def cns(request):
    filter = FilterForm()
    print(filter)
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

@csrf_exempt
def process_variant(request, variant_type, ar_name):
    variant_paths = {"CNV": "cnv", "SNV": "snv", "SV": "sv"}

    if variant_type not in variant_paths:
        return JsonResponse({"success": False, "error": f"Unknown variant type: {variant_type}"})

    try:
        file_path = handle_variant_file(ar_name, variant_paths[variant_type])

        try:
            parse_cns_file(file_path, ar_name)
            print("Parsing complete", file_path)

            try:
                graphic = generate_graph(ar_name, file_path)
                print("Graph generated", graphic)
                return JsonResponse({"success": True, "graphic": graphic})

            except Exception as graph_error:
                return JsonResponse({
                    "success": False,
                    "error": f"Graph generation failed: {str(graph_error)}",
                    "stage": "graph_generation"
                })

        except Exception as parse_error:
            return JsonResponse({
                "success": False,
                "error": f"File parsing failed: {str(parse_error)}",
                "stage": "parsing"
            })

    except Exception as file_error:
        return JsonResponse({
            "success": False,
            "error": f"File handling failed: {str(file_error)}",
            "stage": "file_handling"
        })

@csrf_exempt
def import_cns(request, ar_name):
    folders = ["cnv/output", "snv/output", "alignment/output"]
    folder_stats = []
    total_stats = {
        "folder_name": "Total",
        "success_count": 0,
        "failed_count": 0,
        "objects_created": 0,
    }

    try:
        for folder in folders:
            current_stats = {
                "folder_name": folder,
                "success_count": 0,
                "failed_count": 0,
                "objects_created": 0,
            }

            try:
                cns_files = handle_variant_file(ar_name, folder)

                for file_path in cns_files:
                    try:
                        created_objects_count = parse_cns_file(file_path, ar_name)
                        current_stats["success_count"] += 1
                        current_stats["objects_created"] += created_objects_count
                    except Exception as parse_error:
                        current_stats["failed_count"] += 1
                        print(f"Error parsing file {file_path}: {str(parse_error)}")

            except Exception as folder_error:
                current_stats["failed_count"] = 1  # Count the folder itself as a failure
                print(f"Error processing folder {folder}: {str(folder_error)}")

            # Update total statistics
            total_stats["success_count"] += current_stats["success_count"]
            total_stats["failed_count"] += current_stats["failed_count"]
            total_stats["objects_created"] += current_stats["objects_created"]
            folder_stats.append(current_stats)

        folder_stats.append(total_stats)
        return JsonResponse({"success": True, "summary": folder_stats})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
