import os
import re
from django.conf import settings
import shutil
from sequencingfile.models import SequencingFile, SequencingFileSet
from django.core.exceptions import ObjectDoesNotExist
from collections import defaultdict
from collections import defaultdict


def generate_prefix(x):
    prefix = "*"*30
    match = re.match(r'(\w+)[-_]([ACTG]{6,8}(?:-[ACTG]{6,8})?)', x)
    if match:
        dna = match.group(2)
        prefix = x.split(dna)[0] + dna
    elif ".fastq" in x:
        prefix = x.split("_L0")[0]
        if "." in prefix:
            prefix = x.split("_R")[0]
    elif ".sorted" in x:
        prefix = x.split(".sorted")[0]
    elif "deduplicated.realign.bam" in x:
        prefix = x.split(".deduplicated.realign.bam")[0]
    elif ".bam" in x and "deduplicated" not in x:
        prefix = x.split(".bam")[0]
        if "." in prefix:
            prefix = x.split(".sortq")[0]
    elif ".bai" in x and not ".bam" in x:
        prefix = x.split(".bai")[0]

    if "." not in prefix:
        return prefix
    return



def get_file_tree(file_list, path, sequencing_run, sample_libs):
    try:
        sample_dict = defaultdict(list)
        for file in file_list:
            for sample in sample_libs:
                if sample.name in file:  # Check if sample name is in file name
                    sample_dict[sample.name].append(file)
        return sample_dict
    except ObjectDoesNotExist as e:
        print(e)
        return


def get_file_sets(sequencing_run, sample_libs):
    files = os.path.join(settings.HISEQDATA_DIRECTORY, sequencing_run.name)

    # print(files)
    file_list = []
    file_sets = defaultdict(list)
    for root, dirs, files in os.walk(files):
        # print(root,dirs,files)
        for file in files:
            # print(file)
            if file.strip().endswith(".fastq.gz") | file.strip().endswith(".bam") | file.strip().endswith(".bai"):
                file_list.append(file)
    print(get_file_tree(file_list, root, sequencing_run, sample_libs))
    return [{'file_set': key, 'files': value} for key, value in get_file_tree(file_list, root, sequencing_run, sample_libs).items()]

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
