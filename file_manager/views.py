import json
from django.views import View
from .models import FileManager
from .serializer import *
from core.decorators import permission_required_for_async
from django.http import JsonResponse

def list_files(request):
    return render(request, "files_list.html", locals())


@permission_required_for_async("cns.view_cns")
def filter_files(request):
    directories = FileManager.objects.query_by_args(**request.GET)

    serializer = FileDirectorySerializer(directories['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = directories['draw']
    result['recordsTotal'] = directories['count']
    result['recordsFiltered'] = directories['total']
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
