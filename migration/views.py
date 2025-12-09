from django.shortcuts import render
from .forms import *
from django.http import HttpResponse, JsonResponse
from lab.models import Patient
from blocks.models import Block
from projects.models import Project
from areas.models import Area
from libprep.models import NucAcids
from samplelib.models import SampleLib, NA_SL_LINK
from capturedlib.models import CapturedLib, SL_CL_LINK
from bait.models import Bait
from barcodeset.models import Barcode
from sequencingrun.models import SequencingRun
from sequencinglib.models import SequencingLib,CL_SEQL_LINK
from sequencingfile.models import SequencingFile, SequencingFileSet
from variant.models import *
from gene.models import *
from body.models import *
from django.core.exceptions import ObjectDoesNotExist
import json
import xlrd
import string
import random
from itertools import groupby,chain
import re
import ast
from pathlib import Path
import pandas as pd
import os
import django
from django.db.models import Count, Min

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
django.setup()


def sequenced_files(request):
    import csv
    from io import StringIO


    if request.method == "POST":
        form = SequencedFilesForm(request.POST, request.FILES)

        if form.is_valid():
            report = []
            log = []

            file1 = request.FILES["checksum_file"]
            file2 = request.FILES["tree2_file"]

            checksum_dataset = json.loads(file1.read())
            tree2_dataset = json.loads(file2.read())

            for sample_lib in SampleLib.objects.all():

                status = "OK"

                checksum = None
                for c in checksum_dataset:
                    if c["sl_id"] == sample_lib.name:
                        checksum = c["checksum"]
                        break

                filename = None
                for t in tree2_dataset:
                    if t["sl_id"] == sample_lib.name:
                        filename = t["filename"]
                        break

                # sequencing_run = sample_lib.sl_cl_links.first().captured_lib.cl_seql_links.first().sequencing_lib.sequencingrun_set.first()
                sequencing_run_name = None
                sl = sample_lib.sl_cl_links.first()
                if sl:
                    cl = sl.captured_lib.cl_seql_links.first()
                    if cl:
                        sequencing_run_name = cl.sequencing_lib.sequencingrun_set.first().name

                if not filename:
                    status = "missing sequencing files"

                if not checksum:
                    if filename:
                        status = "missing checksum"
                    else:
                        status += ",missing checksum"

                report.append({
                    "sample_lib":sample_lib.name,
                    "directory":sequencing_run_name,
                    "filename":filename,
                    "checksum":checksum,
                    "status":status
                })

            response = HttpResponse(
                content_type='text/csv',
                headers={'Content-Disposition': 'attachment; filename="report-seq-files.csv"'},
            )

            field_names = ["sample_lib","directory","filename","checksum","status"]
            writer = csv.writer(response)
            writer.writerow(field_names)
            for item in report:
                writer.writerow([item[field] for field in field_names])

            return response
    else:
        form = SequencedFilesForm()

    return render(request,"sequenced_files.html",locals())

def sequenced_files_opposite(request):
    import csv
    from io import StringIO

    if request.method == "POST":
        form = SequencedFilesForm(request.POST, request.FILES)

        if form.is_valid():
            report = []
            log = []

            file1 = request.FILES["checksum_file"]
            file2 = request.FILES["tree2_file"]

            checksum_dataset = json.loads(file1.read())
            tree2_dataset = json.loads(file2.read())

            for t in tree2_dataset:
                status = "OK"

                checksum = None
                for c in checksum_dataset:
                    if c["sl_id"] == t["sl_id"]:
                        checksum = c["checksum"]
                        break

                sequencing_run_name = None
                try:
                    sample_lib = SampleLib.objects.get(name=t["sl_id"])
                    sl = sample_lib.sl_cl_links.first()
                    if sl:
                        cl = sl.captured_lib.cl_seql_links.first()
                        if cl:
                            sequencing_run_name = cl.sequencing_lib.sequencingrun_set.first().name
                except Exception as e:
                    sample_lib = None
                    status = "does not exists in database"

                if not checksum:
                    if sample_lib:
                        status = "missing checksum"
                    else:
                        status += ",missing checksum"

                report.append({
                    "sample_lib":t["sl_id"],
                    "directory":sequencing_run_name,
                    "filename":t["filename"],
                    "checksum":checksum,
                    "status":status
                })

            response = HttpResponse(
                content_type='text/csv',
                headers={'Content-Disposition': 'attachment; filename="report-seq-files-v3.csv"'},
            )

            field_names = ["sample_lib","directory","filename","checksum","status"]
            writer = csv.writer(response)
            writer.writerow(field_names)
            for item in report:
                writer.writerow([item[field] for field in field_names])

            return response
    else:
        form = SequencedFilesForm()

    return render(request,"sequenced_files.html",locals())

def variant(request):
    def get_value_by_startswith(v,k):
        for t in v.split(":"):
            if t.startswith(k):
                return t.strip()
        return None

    if request.method == "POST":
        form = VariantForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            lines = file.readlines()
            cols = str(lines[0]).split("\\t")
            # for i,col in enumerate(cols):
            #     print("%s(%d)" % (col.strip(),i))
            for line in lines[1:]:
                values = str(line).split("\\t")

                variant_call = VariantCall.objects.create(
                    coverage = values[59],
                    ref_read = values[60],
                    alt_read = values[61],
                )

                g_variant = GVariant.objects.create(
                    variant_call = variant_call,
                    chrom = values[0],
                    start = values[1],
                    end = values[2],
                    ref = values[3],
                    alt = values[4],
                    avsnp150 = values[29]
                )

                for value in values[9].split(","):
                    print(value.strip()) #ALK:NM_004304:exon16:c.T2743G:p.W915G

                    parts =  value.split(":")

                    if len(parts)>1:
                        c_variant = CVariant.objects.create(
                            g_variant = g_variant,
                            gene =parts[0].strip(),
                            nm_id = parts[1].strip(),
                            c_var = get_value_by_startswith(value,"c."),
                            exon = get_value_by_startswith(value,"exon").split("exon")[1],
                            func = values[5],
                            gene_detail = values[7]
                        )

                        p_var = get_value_by_startswith(value,"p.")

                        p_variant = PVariant.objects.create(
                            c_variant = c_variant,
                            ref = p_var.split("p.")[1][1],
                            pos = p_var.split("p.")[1][:-1],
                            alt = p_var.split("p.")[1][-1]
                        )

    else:
        form = VariantForm()
    return render(request, "variant.html", locals())

def gene(request):
    def get_int_value(v):
        try:
            return int(v)
        except Exception as e:
            return 0

    if request.method == "POST":
        form = GeneForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            lines = file.readlines()
            cols = str(lines[0]).split("\\t")

            # for i,col in enumerate(cols):
            #     print("%s(%d)" % (col.strip(),i))

            for line in lines[1:]:
                values = str(line).split("\\t")

                try:
                    gene = Gene.objects.create(
                        name = values[2],
                        chr = values[10],
                        start = get_int_value(values[12]),
                        end = get_int_value(values[13]),
                    )

                    print("created for ", gene.__dict__)
                except Exception as e:
                    print(values[6])
                    print(len(values[6]))
                    raise
    else:
        form = GeneForm()
    return render(request, "gene.html", locals())

def import_body_sites(request):
    if request.method == "POST":
        form = BodySitesForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            xl_workbook = xlrd.open_workbook(file_contents=file.read())
            sheet_names = xl_workbook.sheet_names()
            xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])
            data = [[xl_sheet.row(i)[j].value for j in range(0,xl_sheet.ncols)] for i in range(1,xl_sheet.nrows)]
            for row in data:
                parent = None
                for i in range(len(row)-1,-1,-1):
                    num = 10 - (i + 6)
                    name = str(num) + "-" + row[i]
                    print(name)
                    parent, created = Body.objects.get_or_create(
                        name=name,
                        parent=parent
                    )
    else:
        form = BodySitesForm()

    return render(request,"body_sites.html", locals())

def get_or_cons(row):
    print(row["Sample"])
    SampleLib.objects.get(name="")

def qpcr_consolidated_data(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "Consolidated_data_final.csv")
    df = pd.read_csv(file)
    # df[~df["Input Conc."].isnull()].apply(lambda row: get_or_cons(row), axis=1)
    df.iloc[:48].apply(lambda row: get_or_cons(row), axis=1)

def get_at_na(row):
    print(row['NA_ID'], row['Shearing volume DNA input (ul)'])
    try:
        if not pd.isnull(row['Shearing volume DNA input (ul)']):
            for sl in row["SL_ID"].split(","):
                SampleLib.objects.filter(name=sl.strip()).update(shear_volume=float(row['Shearing volume DNA input (ul)']),
                                                                 amount_in=float(row['NA sheared/used (ng)']))
    except Exception as e:
        print(e)

def qpcr_at_na(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "Nucleic Acids-Grid view (1).csv")
    df = pd.read_csv(file)
    df[~df["NA_ID"].isnull()].apply(lambda row: get_at_na(row), axis=1)

def get_at_sl(row):
    print(row['SL_ID'])
    try:
        SampleLib.objects.filter(name=row['SL_ID']).update(
            qubit=float(row['Post-lib Qubit (ng/ul)']),
            qpcr_conc=float(row['Post-lib qPCR (ng/ul)']),
            pcr_cycles=float(row['Pre-hyb PCR cycles']),
            amount_final=float(row['Total LP DNA for capture (ng)']),
            vol_init=float(row['Volume of library (ul)']),
            notes=row['Notes'],
        )

    except Exception as e:
        print(e)
    if pd.isnull(row['Post-hyb PCR cycles']):
        return
    try:
        print(row["CL_ID"])
        if "," in row["CL_ID"]:
            for cl in row["CL_ID"].split(","):
                print(row["CL_ID"])
                CapturedLib.objects.filter(name=cl.strip()).update(
                    amp_cycle=float(row['Post-hyb PCR cycles']),
                    notes=row['Notes']
                )
        else:
            CapturedLib.objects.filter(name=row["CL_ID"]).update(
                amp_cycle=float(row['Post-hyb PCR cycles'])
            )
    except Exception as e:
        print(e)

def qpcr_at_sl(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "Sample Library with grid view, analysis view and more-Grid view (2).csv")
    df = pd.read_csv(file)
    df[~df["SL_ID"].isnull()].apply(lambda row: get_at_sl(row), axis=1)

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
            SequencingFileSet.objects.get_or_create(prefix=prefix, path=y)
        except:
            pass
        return prefix
    return

def get_fastq_empty(row):
    try:
        sl = SampleLib.objects.get(name=row["sample_lib"])
        sr = SequencingRun.objects.get(name=row["sequencing_run"])
        files = SequencingFile.objects.filter(sequencing_file_set__sample_lib=sl, sequencing_file_set__sequencing_run=sr, type="fastq")
        for file in files:
            if file.name not in row["fastq_file"]:
                print(sl.name, file, row["fastq_file"])
    except Exception as e:
        print(row["sample_lib"], row["sequencing_run"], e)

def get_fastq_t12(row):
    try:
        sl=SampleLib.objects.get(name=row["sample_lib"])
    except ObjectDoesNotExist as e:
        sl, created = SampleLib.objects.get_or_create(
            name=row["sample_lib"]
        )
    try:
        sr=SequencingRun.objects.get(name=row["sequencing_run"])
    except ObjectDoesNotExist as e:
        sr=SequencingRun.objects.get(name="Undefined")

    if pd.isnull(row["fastq_file"]):
        files=SequencingFile.objects.filter(sequencing_file_set__sample_lib=sl, type="fastq")
        if files.count()>0:
            d={}
            for file in files:
                d[file.name] = file.checksum
            row["fastq_file"] = d
            row["fastq_path"] = file.sequencing_file_set.path
    else:
        files=SequencingFile.objects.filter(sequencing_file_set__sample_lib=sl,
                                            sequencing_file_set__sequencing_run=sr,
                                            type="fastq")
        for file in files:
            if file.name not in row["fastq_file"]:
                d=row["fastq_file"]
                d[file.name]=file.checksum
                row["fastq_file"]=d

    if pd.isnull(row["bam_file"]):
        files=SequencingFile.objects.filter(sequencing_file_set__sample_lib=sl, type="bam")
        if files.count()>0:
            s={}
            for file in files:
                s[file.name] = file.checksum
            row["bam_file"] = s
            row["bam_file_path"] = file.sequencing_file_set.path
    else:
        files=SequencingFile.objects.filter(sequencing_file_set__sample_lib=sl,
                                            sequencing_file_set__sequencing_run=sr,
                                            type="bam")
        for file in files:
            if file.name not in row["bam_file"]:
                d=row["bam_file"]
                d[file.name]=file.checksum
                row["bam_file"]=d

    if pd.isnull(row["bam_bai_file"]):
        files=SequencingFile.objects.filter(sequencing_file_set__sample_lib=sl, type="bai")
        if files.count()>0:
            w={}
            for file in files:
                w[file.name] = file.checksum
            row["bam_bai_file"] = w
            row["bam_bai_file_path"] = file.sequencing_file_set.path
    else:
        files=SequencingFile.objects.filter(sequencing_file_set__sample_lib=sl,
                                            sequencing_file_set__sequencing_run=sr,
                                            type="bai")
        for file in files:
            if file.name not in row["bam_bai_file"]:
                d=row["bam_bai_file"]
                d[file.name]=file.checksum
                row["bam_bai_file"]=d

    return row

def get_bam_empty(row):
    print(row["sample_lib"])
    try:
        sl=SampleLib.objects.get(name=row["sample_lib"])
    except ObjectDoesNotExist as e:
        sl, created = SampleLib.objects.get_or_create(
            name=row["sample_lib"]
        )
    if pd.isnull(row["bam_file"]):
        files=SequencingFile.objects.filter(sequencing_file_set__sample_lib=sl, type="bam")
        if files.count()>0:
            d={}
            for file in files:
                d[file.name] = file.checksum
            row["bam_file"] = d
            row["bam_file_path"] = file.sequencing_file_set.path
            return row

def get_bai_empty(row):
    try:
        sl = SampleLib.objects.get(name=row["sample_lib"])
    except ObjectDoesNotExist as e:
        sl, created = SampleLib.objects.get_or_create(
            name=row["sample_lib"]
        )
    if pd.isnull(row["bam_bai_file"]):
        files=SequencingFile.objects.filter(sequencing_file_set__sample_lib=sl, type="bai")
        if files.count()>0:
            d={}
            for file in files:
                d[file.name] = file.checksum
            row["bam_bai_file"] = d
            row["bam_bai_file_path"] = file.sequencing_file_set.path
            return row

def refactor_samplelib(row):
    return ("T"+str(row["Block"])+"_"+str(row["sample_lib"])).replace("-","_")

def find_seq_run(row, df2):
    if not pd.isnull(row["sequencing_run"]):
        return row["sequencing_run"]
    sl = SampleLib.objects.get(name=row["sample_lib"])
    match = df2[df2["HiSeqData/"].str.contains(sl.name, regex=False)]["HiSeqData/"].values
    if len(match)>1:
        seq_run = match[0].strip().split("-->")[0].split("/")[1]
        print(seq_run)
        return seq_run

def split_and_extract(s):
    match = re.search("[ATGC]{6}", s)
    if match:
        return s.split('_' + match.group() + '_')[0]
    else:
        return s  # Or return None if you want to filter out non-matching strings

def get_sex(value):
    return value.lower() if value and len(value) == 1 else None

def get_race(value):
    for x in Patient.RACE_TYPES:
        if value.lower() == x[1].lower():
            return x[0]
    return 7

def get_or_create_patient(**kwargs):
    try:
        return Patient.objects.get(pat_id=kwargs["pat_id"])
    except ObjectDoesNotExist as e:
        return Patient.objects.create(**kwargs)

def get_area_type(value):
    for x in Area.AREA_TYPE_TYPES:
        if value.lower() == x[1].lower():
            return x[0]
    return None

def patients(row):
    try:

        blocks = Block.objects.filter(patient__isnull=True)
        for block in blocks:
            patient_id = "_G"
            patient, created = Patient.objects.get_or_create(pat_id=patient_id)
            block.patient = patient
            block.save()
            print("created")
    except Exception as e:
        print(row["block"],e)

def check_patient(request):
    from .migrate_dump import MigrateDump
    # SampleLib.objects.filter().delete()
    # MigrateDump.register_patients()
    MigrateDump.register_samplelib()
    # for na in NucAcids.objects.all():
    #     print(na)
    #     obj, created = AREA_NA_LINK.objects.get_or_create(nucacid=na,area=na.area)
    # file = Path(Path(__file__).parent.parent / "uploads" / "report_patients_not_matched.csv")
    # df = pd.read_csv(file)
    # df.apply(lambda row: patients(row), axis=1)

def check_blocks(row):
    try:
        print(row["name"])
        b = Block.objects.get(name=row["name"])
        b.age=row["pat_age"] if not pd.isnull(row["pat_age"]) else b.age
        b.thickness=row["thickness"] if not pd.isnull(row["thickness"]) else b.thickness
        b.mitoses=row["mitoses"] if not pd.isnull(row["mitoses"]) else b.mitoses
        b.p_stage=row["p_stage"] if not pd.isnull(row["p_stage"]) else b.p_stage
        b.prim=row["prim"] if not pd.isnull(row["prim"]) else b.prim
        b.subtype=row["subtype"] if not pd.isnull(row["subtype"]) else b.subtype
        b.notes=row["note"] if not pd.isnull(row["note"]) else b.notes
        b.micro=row["micro"] if not pd.isnull(row["micro"]) else b.micro
        b.save()
    except Exception as e:
        print(row["name"],e)

def check_block(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "report-block.csv")
    df = pd.read_csv(file)
    df.apply(lambda row: check_blocks(row), axis=1)

def get_collection(value):
    for x in Block.COLLECTION_CHOICES:
        if value.lower() == x[1].lower():
            return x[0]
    return Block.SCRAPE

def create_abbreviation(value):
    words = value.split()
    result = ''.join(word[0] for word in words)
    result_upper = result.upper()
    projects = Project.objects.filter(abbreviation=result_upper)
    if projects:
        words = value.split()
        result = ''.join(word[:2] for word in words)
        result_upper = result.upper()[::-1]
    # print(value, result_upper)
    return result_upper[:6]

def blocks_sl_at_get(row):
    try:
        patient = Patient.objects.get(pat_id=str(row["Pat_ID"]))
        if not pd.isnull(row['Block_ID']):
            for b in row['Block_ID'].replace(";",",").split(","):
                block = Block.objects.get(name=b.strip())
                block.patient = patient
                block.save()
        else:
            for a in row['Area_ID'].replace(";", ",").split(","):
                area = Area.objects.get(name=a.strip())
                block = area.block
                if block.name != "UndefinedBlock":
                    block.patient = patient
                    block.save()
        # block = Block.objects.get(name=row['Block_ID'].strip())
        # if not pd.isnull(row['Pat_ID']):
        #     patient = Patients.objects.get(pat_id=str(row["Pat_ID"]))
        #     # print(block.strip())
        #     block.patient = patient
        #     block.save()
    except Exception as e:
        print(e, row["Pat_ID"], row['Block_ID'], row['Area_ID'])

def blocks_sl_at(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "Sample Library with grid view, analysis view and more-Grid view (5).csv")
    file2 = Path(Path(__file__).parent.parent / "uploads" / "Consolidated_data_final.csv")
    df = pd.read_csv(file)
    df2 = pd.read_csv(file)
    df.apply(lambda row: blocks_sl_at_get(row), axis=1)

def im_ar_types(row):
    try:
        area = Area.objects.get(id=int(row['data-1715715228037']))
        area.area_type = row["Unnamed: 2"].lower()
        area.save()
    except:
        print(row)

def im_bait(row):
    # print(row["bait"], row["CL"])
    try:
        cl = CapturedLib.objects.get(name=row["CL"])
        bait = Bait.objects.get(name=row["Bait"])
        if cl.bait is None:
            cl.bait = bait
            cl.save()
    except Exception as e:
        print(e, row["Bait"])

def generate_file_set(file, seq_run, sample_lib):
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
        prefix = file.split(".bai")[0]
    elif file.endswith(".bam"):
        file_type = "bam"
        prefix = file.split(".bam")[0]
    if match:
        dna = match.group(1)
        prefix = file.split(dna)[0] + dna
    if prefix is None:
        prefix = file.split(".")[0]
    file_set, _ = SequencingFileSet.objects.get_or_create(prefix=prefix,
                                                          sequencing_run=seq_run,
                                                          sample_lib=sample_lib)
    print("file_set generated", prefix, "------", file)
    return file_set


def read_genes():
    file = Path(Path(__file__).parent.parent / "uploads" / "gene_past_version.csv")
    df = pd.read_csv(file)
    # df[~df["Input Conc."].isnull()].apply(lambda row: get_or_cons(row), axis=1)
    print(df)
    for i,row in df.iterrows():
        gene = Gene.objects.get(id=row["id"])
        gene.name = row["name"]
        gene.save()
        print(gene.name)

def import_genes(request):
    from .glacier_convert import convert_prefix
    print("convert_to_standard...")
    convert_prefix()
    # from .variant_call_alias import restore_variant_files
    # restore_variant_files()


def import_file_tree(request):
    duplicate_foobars = (
        GVariant.objects
        .values('start', 'chrom', 'ref', 'alt')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
    )

    for dup in duplicate_foobars:
        start = dup['start']
        chrom = dup['chrom']
        ref = dup['ref']
        alt = dup['alt']

        # Find all duplicate GVariant IDs for this group
        duplicates = GVariant.objects.filter(
            start=start, chrom=chrom, ref=ref, alt=alt
        ).values_list('id', flat=True)

        min_id = min(duplicates)

        # Update all VariantCalls that reference the duplicate GVariants
        VariantCall.objects.filter(g_variant_id__in=duplicates).update(g_variant_id=min_id)

        # Delete all GVariants except the one with min ID
        deleted, _ = GVariant.objects.filter(id__in=duplicates).exclude(id=min_id).delete()

        print(
            f"✅ Assigned VariantCalls to GVariant ID {min_id}; Deleted {deleted} duplicates for ({chrom}, {start}, {ref}, {alt})")

    return HttpResponse("Deduplication complete.")


