import json
from django.views import View
from .models import FileManager
from .serializer import *
from core.decorators import permission_required_for_async
from django.http import JsonResponse
from django.core.cache import cache
import hashlib


def list_files(request):
    return render(request, "files_list.html", locals())


@permission_required_for_async("file_mamanger.view_file_manager")
def filter_files(request):
    # Extract the 'sub_dir' and 'exact_dir' from request.GET
    sub_dir = request.GET.get('sub_dir', '')
    exact_dir = request.GET.get('exact_dir', '')

    # Create a dictionary with only 'sub_dir' and 'exact_dir' for caching purposes
    filtered_params = {
        'sub_dir': sub_dir,
        'exact_dir': exact_dir,
    }

    # Generate a stable cache key using only these parameters
    cache_key_raw = json.dumps(filtered_params, sort_keys=True)
    cache_key = "filter_files:" + hashlib.md5(cache_key_raw.encode()).hexdigest()

    print("\n"*5)
    print("cache_key_raw: ", cache_key_raw)
    print("cache_key: ", cache_key)

    # Try to get cached data
    result = cache.get(cache_key)

    if result is None:
        print("Cache miss. Querying database.")
        directories = FileManager.objects.query_by_args(**request.GET)
        serializer = FileDirectorySerializer(directories['items'], many=True)
        result = {
            'data': serializer.data,
            'draw': directories['draw'],
            'recordsTotal': directories['count'],
            'recordsFiltered': directories['total'],
        }
        # Cache the result for 5 minutes
        cache.set(cache_key, result, timeout=300)
    else:
        print("Cache hit.")

    return JsonResponse(result)


class ListDirectoriesView(View):
    """API to list all directories in SMB"""
    def get(self, request, sub_dir=""):
        directories = FileManager.objects.list_directories(sub_dir)
        return JsonResponse({"directories": directories})


class CreateDirectoryView(View):
    """API to create a new directory in SMB"""
    def post(self, request):
        data = json.loads(request.body)
        directory_name = data.get("directory_name", "")
        result = FileManager.objects.create_directory(directory_name)
        return JsonResponse({"message": f"Directory created: {result}"})


class DeleteFileView(View):
    """API to delete a file"""
    def post(self, request):
        data = json.loads(request.body)
        file_path = data.get("file_path", "")
        result = FileManager.objects.delete_file(file_path)
        return JsonResponse({"message": result})


class MoveFileView(View):
    """API to move a file"""
    def post(self, request):
        data = json.loads(request.body)
        src = data.get("src", "")
        dst = data.get("dst", "")
        result = FileManager.objects.move_file(src, dst)
        return JsonResponse({"message": result})
from django.shortcuts import render

# Create your views here.
