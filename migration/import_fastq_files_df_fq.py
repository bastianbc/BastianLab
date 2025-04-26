import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
django.setup()
from django.http import HttpResponse
from django.db import IntegrityError
from samplelib.models import SampleLib, NA_SL_LINK
from capturedlib.models import CapturedLib, SL_CL_LINK
from sequencingrun.models import SequencingRun
from sequencinglib.models import SequencingLib,CL_SEQL_LINK
from sequencingfile.models import SequencingFile, SequencingFileSet
from body.models import *
import json
import re
from pathlib import Path
import pandas as pd


def match_respectively_via_names(sl,files):
    l = ["16","19","20","21","22","23","24","25","28","89","AGLP","AM-",
         "CCRLP-","CGH","ChIP","CGP","FKP","DPN","DM","EXLP","H12","Ivanka","JBU","IRLP",
         "JJS","Kit","NMLP","OMLP","Rob","SGLP","VMRLP","UM","T12","XD","XuRLP"]
    if sl.name.startswith(tuple(l)):
        if sl.name.startswith(tuple(["21_5","24_5_Norm","28"])):
            return
        # print(sl.name)
        for file in files:
            file_set = file.sequencing_file_set
            file_set.sample_lib = sl
            file_set.save()
            print("saved = ", sl)

def match_sl_fastq_file_1(request):
    sls = SampleLib.objects.filter(sequencing_file_sets__isnull=True).order_by("name")
    data=[]
    for sl in sls:
        match = SequencingFile.objects.filter(name__icontains=sl.name)
        if match:
            match_respectively_via_names(sl,match)
            row = {
                "sample_lib": sl.name,
                "file": match.values_list('name')
            }
            data.append(row)
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="result.csv"'

    # Write DataFrame to the response as a CSV
    df.to_csv(path_or_buf=response, index=False)

    print("--FIN--")
    return response

def match_sl_fastq_file_2(request):
    def process_files(sl, files, description):
        """
        Process the matched files by updating the sample_lib field
        and print debug information.
        """
        print(f"{description}: {sl.name}, Files Found: {files.count()}")
        for file in files:
            print(f"{sl.name} --- {file.name}")
            file_set = file.sequencing_file_set
            file_set.sample_lib = sl
            file_set.save()
            print(f"Saved Sample Library: {sl.name}")


    sls = SampleLib.objects.filter(sequencing_file_sets__isnull=True).order_by("name")
    print(sls.count())
    data=[]
    patterns = [
        (re.compile(r'^(\w+)-(\d{1,3})$'), lambda match: fr'^{match.group(1)}-(?<!0){match.group(2)}(_|$)',
         'Regex Match'),
        (re.compile(r'^26\d*_(\w+)$'), lambda _: sl.name, 'Startswith 26'),
        (re.compile(r'^28_'), lambda _: sl.name, 'Startswith 28'),
        (re.compile(r'^Buffy_Coat'), lambda _: sl.name, 'Buffy_Coat'),
        (re.compile(r'^ChIP1_(\d{1,2})$'), lambda match: fr'^ChIP1_-(?<!0){match.group(1)}(_|$)', 'Regex Match ChIP1_'),
        (re.compile(r'^KAM(.*?)(_kapa)?$'), lambda match:(f'^KAM{match.group(1)}' + (match.group(2) or '')), 'Regex Match KAM'),
    ]

    for sl in sls:
        for pattern, search_func, description in patterns:
            match = pattern.match(sl.name)
            print(sl.name, match)
            if match:
                search_value = search_func(match)
                filter_kwargs = {'name__regex': search_value} if description == 'Regex Match' else {
                    'name__startswith': search_value} if description == 'Startswith 26' else {
                    'name__startswith': search_value} if description == 'Startswith 28' else {
                    'name__icontains': search_value} if description == 'Buffy_Coat' else {
                    'name__regex': search_value} if description == 'Regex Match ChIP1_' else {
                    'name__regex': search_value}
                print(filter_kwargs)
                files = SequencingFile.objects.filter(**filter_kwargs)
                if files:
                    process_files(sl, files, description)



def generate_file_set(file, path, sample_lib, seq_run):
    try:
        match = re.match(r'.*[-_]([ACTG]{6,8})[-_]', file)
        file_type = ""
        if "fastq" in file:
            file_type = "fastq"
            prefix = file.split("_L0")[0] if "_L0" in file else file.split("_001")[0] if "_001" in file else None
        elif ".sorted" in file:
            file_type = "bam"
            prefix = file.split(".sorted")[0]
        elif ".sort" in file:
            file_type = "bam"
            prefix = file.split(".sort")[0]
        elif ".removedupes" in file:
            file_type = "bam"
            prefix = file.split(".removedupes")[0]
        elif ".recal" in file:
            file_type = "bam"
            prefix = file.split(".recal")[0]
        elif "deduplicated.realign.bam" in file:
            file_type = "bam"
            prefix = file.split(".deduplicated.realign.bam")[0]
        elif file.endswith(".bai"):
            file_type = "bai"
            prefix = file.split(".")[0]
        elif file.endswith(".bam"):
            file_type = "bam"
            prefix = file.split(".")[0]
        if match:
            dna = match.group(1)
            prefix = file.split(dna)[0] + dna
        if prefix is None:
            prefix = file.split(".")[0]
        file_set, _ = SequencingFileSet.objects.get_or_create(prefix=prefix)
        file_set.sample_lib = sample_lib
        file_set.sequencing_run = seq_run
        file_set.path = path
        file_set.save()
        print("file_set generated", prefix, "------", file)
        return file_set
    except Exception as e:
        print(f"Fileset not created {file} {e}")
        return None


def find_sample(file_name):
    try:
        match = re.match(r"^(.*?)(?:_S|\.)", file_name)
        if match and re.search(r"\b(bam|bai)\b", file_name):
            return SampleLib.objects.get(name=match.group(1))
    except:
        print(f"Sample not found {file_name}")
        return None

def find_seqrun(path):
    try:
        sr_name = path.split("/")[1]
        return SequencingRun.objects.get(name=sr_name)
    except:
        print(f"Seq Run not found {path}")
        return None

def get_file_set(sr, sl):
    try:
        SequencingFileSet.objects.get(sequencing_run=sr, sample_lib=sl)
    except:
        print(f"SequencingFileSet not found {sr, sl}")

def register_new_fastq_files():
    file = Path(Path(__file__).parent / "df_fq0421.csv")
    df = pd.read_csv(file)
    df = df.reset_index()
    for index, row in df.iterrows():
        file, created = SequencingFile.objects.get_or_create(name=row['file'])
        if file.sequencing_file_set:
            if not file.sequencing_file_set.sequencing_run or not file.sequencing_file_set.sample_lib:
                print("SL % SR missing", file.name)
                sl = find_sample(row['file'])
                sr = find_seqrun(row['path'])
                fs = SequencingFileSet.objects.get(prefix=file.sequencing_file_set.prefix)
                fs.sample_lib = sl
                fs.sequencing_run = sr
                fs.save()
                if "fastq" in row['file'].lower():
                    _type = "fastq"
                elif "bai" in row['file'].lower():
                    _type = "bai"
                else:
                    _type = "bam"

                if not fs.path:
                    fs.path = row['path']
                    fs.save()
                file.type = _type
                file.save()
            continue

        else:
            sl = find_sample(row['file'])
            sr = find_seqrun(row['path'])
            file_set = generate_file_set(row['file'],row['path'], sl, sr)
            file.sequencing_file_set = file_set
            if "fastq" in row['file'].lower():
                _type = "fastq"
            elif "bai" in row['file'].lower():
                _type = "bai"
            else:
                _type = "bam"

            file.type = _type
            file.save()







def get_or_create_seqrun(name):
    if name:
        obj, created = SequencingRun.objects.get_or_create(
            name=name
        )
        return obj
    return None

def create_seq_run(row):
    print(row["Sequencing Run_ID"])
    if "," in row["Sequencing Run_ID"]:
        for seqrun in row["Sequencing Run_ID"].split(','):
            get_or_create_seqrun(name=seqrun)
    else:
        get_or_create_seqrun(name=row["Sequencing Run_ID"])


def qpcr_at_seqrun(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "Sample Library with grid view, analysis view and more-Grid view (3).csv")
    df = pd.read_csv(file)
    df[~df["Sequencing Run_ID"].isnull()].apply(lambda row: create_seq_run(row), axis=1)


def checkfiles(row):
    try:
        SequencingFileSet.objects.get(prefix=next(iter(row['fastq_file'])).split("_L0")[0])
    except Exception as e:
        print(e, row['sample_lib'])

def make_dict(d):
    try:
        return json.loads(d)
    except:
        return None

def get_or_create_set(prefix, path, sample_lib, sequencing_run):
    if prefix:
        obj, created = SequencingFileSet.objects.get_or_create(
            prefix=prefix,
            path=path,
            sample_lib=sample_lib,
            sequencing_run=sequencing_run
        )
        return obj
    return None

def get_or_create_file(sequencing_file_set, name, checksum, type):
    if sequencing_file_set:
        obj, created = SequencingFile.objects.get_or_create(
            sequencing_file_set=sequencing_file_set,
            name=name,
            checksum=checksum,
            type=type
        )
        return obj
    return None

def get_or_create_cl(sl, name):
    if name:
        obj, created = CapturedLib.objects.get_or_create(
            name=name,
            samplelib=sl
        )
        return obj
    return None

def get_or_create_seql(cl, name):
    if name:
        obj, created = SequencingLib.objects.get_or_create(
            name=name,
            captured_lib=cl
        )
        return obj
    return None

def get_or_create_files_from_file(row):
    prefix = next(iter(row['fastq_file'])).split("_L0")[0]
    try:
        set_ = get_or_create_set(
            prefix=prefix,
            path=row['fastq_path'],
            sample_lib=SampleLib.objects.get(name=row["sample_lib"]),
            sequencing_run=SequencingRun.objects.get(name=row["sequencing_run"]),
        )
        for file, checksum in row["fastq_file"].items():
            get_or_create_file(
                sequencing_file_set=set_,
                name=file,
                checksum=checksum,
                type="fastq"
            )
    except Exception as e:
        print(e, row["sample_lib"], row["sequencing_run"])

def get_file_set(prefix):
    try:
        SequencingFileSet.objects.get(prefix=prefix)
    except Exception as e:
        print(e, prefix)

def generate_prefix(x, y):
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
        try:
            file_set, _ = SequencingFileSet.objects.get_or_create(prefix=prefix, path=y)
        except:
            pass

        return prefix
    return

def execute_rules():
    SequencingFileSet.objects.filter(prefix__regex=r'_R\d$').delete()
    SequencingFileSet.objects.filter(prefix__regex=r'[ACTG]{6,8}.*S\d$').delete()
    for fs in SequencingFileSet.objects.filter(sample_lib__isnull=True):
        try:
            match = re.match(r'([ACTG]{6,8})', fs.prefix)
            if match:
                name = fs.prefix.replace(match.group(1),"")
                sl = SampleLib.objects.get(name=name)
                fs.sample_lib = sl
                fs.save()
                print(sl)
            elif re.search(r'S\d$', fs.prefix):
                name = fs.prefix.split("_S")[0]
                sl = SampleLib.objects.get(name=name)
                fs.sample_lib = sl
                fs.save()
                print(sl)
        except Exception as e:
            print(e)

def create_file(file, prefix):
    try:
        fs = SequencingFileSet.objects.get(prefix=prefix)
        file = SequencingFile.objects.create(name=file, sequencing_file_set=fs)
    except IntegrityError as e:
        file = SequencingFile.objects.get(name=file)
        file.sequencing_file_set = fs
        file.save()
        print(f"Saved")
    except Exception as e:
        print(e)

def create_file_from_df_fq():
    execute_rules()
    file = Path(Path(__file__).parent / "df_fq.csv")
    df = pd.read_csv(file)
    print(df.count())
    '''sample_lib
    sequencing_run
    prefix
    type'''
    # df["prefix"] = df.apply(lambda row: generate_prefix(row['file'], row['path']), axis=1)
    # print("$"*10)
    # df["prefix"].apply(lambda x: get_file_set(x))
    # print("#"*10)
    # df.apply(lambda row: create_file(row['file'], row['prefix']), axis=1)
    # print("^"*10)
    # df.to_csv(Path(Path(__file__).parent.parent / "uploads" / "df_fq_prefix.csv"))


if __name__ == "__main__":
    register_new_fastq_files()
    print("fin_"*10)
