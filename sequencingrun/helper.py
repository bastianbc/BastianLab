import os
from django.conf import settings

def get_file_sets():
    from collections import defaultdict
    files = os.listdir(settings.SEQUENCING_FILES_DIRECTORY)
    file_sets = defaultdict(list)
    for file_name in files:
        parts = file_name.split('_')[:2]
        key = '_'.join(parts)
        file_sets[key].append(file_name)
    return [{'file_set': key, 'files': value} for key, value in file_sets.items()]

def add_flag_to_filename(file_name):
    base_name, extension = os.path.splitext(file_name)
    return f"{base_name}_FLAG{extension}"

def get_source_directory():
     return os.path.join(settings.SEQUENCING_FILES_DIRECTORY)

def get_destination_directory(dir_name):
     return os.path.join(settings.SEQUENCING_FILES_DIRECTORY, "HiSeqData","dir_name")
