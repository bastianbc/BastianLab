import os
import re
from django.conf import settings
import shutil
from sequencingfile.models import SequencingFile, SequencingFileSet
from django.core.exceptions import ObjectDoesNotExist
from collections import defaultdict
from collections import defaultdict
from samplelib.models import SampleLib
import boto3
from collections import defaultdict




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
    s3 = boto3.client("s3")
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    path = f"BastianRaid-02/HiSeqData/{sequencing_run.name}/"

    paginator = s3.get_paginator("list_objects_v2")
    file_list = []
    for page in paginator.paginate(Bucket=bucket, Prefix=path):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith((".fastq.gz", ".bam", ".bai")):
                file_list.append(key)
    print(file_list)
    print(sample_libs)
    # Adapt get_file_tree to handle S3 keys
    file_sets = get_file_tree(file_list, path, sequencing_run, sample_libs)
    print(file_sets)
    return [{"file_set": k, "files": v} for k, v in file_sets.items()]


def get_or_create_file_set(sample, sequencing_run, file):
    try:
        prefix, file_type = SequencingFileSet.generate_prefix(file.split("/")[-1])
        fs = SequencingFileSet.objects.filter(
            prefix=prefix
        ).first()
        fs.sequencing_run = sequencing_run
        fs.sample_lib = sample
        fs.path = file.rsplit("/", 1)[0]
        fs.save()
        if not fs:
            fs = SequencingFileSet.objects.create(
                prefix=prefix,
                sequencing_run=sequencing_run,
                sample_lib=sample,
                path=file.split("/")[-1]
            )
        return fs
    except Exception as e:
        print(e)


def get_type(file):
    if file.endswith(".fastq"):
        return "fastq"
    if file.endswith('.bam') and ".bai" not in file:
        return 'bam'
    if file.endswith('.bai') and ".bam" not in file:
        return 'bai'



def get_or_create_file(file, fs):
    try:
        _file = SequencingFile.objects.get(name=file.split("/")[-1])
        _file.sequencing_file_set = fs
        _file.type = get_type(file)
        _file.save()
        if not _file:
            _file = SequencingFile.objects.create(
                sequencing_file_set=fs,
                name=file,
                type=get_type(file)
            )
        return _file
    except Exception as e:
        print(e)



def create_files_and_sets(file_sets, sequencing_run):
    files = []
    for item in file_sets:
        sample_lib = SampleLib.objects.get(name=item['file_set'])
        if item['files']:
            for file in item['files']:
                fs = get_or_create_file_set(sample_lib, sequencing_run, file)
                _file = get_or_create_file(file,fs)
                files.append(_file.name)
    return files



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
