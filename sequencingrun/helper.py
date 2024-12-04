import os
from django.conf import settings
import shutil

def get_file_sets():
    from collections import defaultdict
    files = os.listdir(settings.SEQUENCING_FILES_SOURCE_DIRECTORY)
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
     return os.path.join(settings.SEQUENCING_FILES_SOURCE_DIRECTORY)

def get_destination_directory(directory_name):
    # directory path to create
    directory_path = os.path.join(settings.SEQUENCING_FILES_DESTINATION_DIRECTORY, directory_name)
    # create directory if not exists
    os.makedirs(directory_path, exist_ok=True)

    return directory_path

def file_transfer(sequencing_run,transfers):

    source_dir = get_source_directory()
    destination_dir = get_destination_directory(sequencing_run.name)

    try:
        for transfer in transfers:
            source_file = os.path.join(source_dir,transfer[0])
            destination_file = os.path.join(destination_dir,transfer[1])
            shutil.move(source_file, destination_file)
            success = True
    except Exception as e:
        print(e)
        success = False

    return success, destination_dir

def get_samplelib(file_set):
    return file_set.split("_")[0]
