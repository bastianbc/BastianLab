from django.shortcuts import render, redirect
from .forms import *
from django.http import HttpResponse
from datetime import datetime
import csv
from io import StringIO
from lab.models import Patients
from blocks.models import Blocks
from projects.models import Projects
from account.models import User
from areas.models import Areas
from libprep.models import NucAcids, AREA_NA_LINK
from method.models import Method
from samplelib.models import SampleLib, NA_SL_LINK
from capturedlib.models import CapturedLib, SL_CL_LINK
from bait.models import Bait
from barcodeset.models import Barcodeset,Barcode
from sequencingrun.models import SequencingRun
from sequencinglib.models import SequencingLib,CL_SEQL_LINK
from sequencingfile.models import SequencingFile, SequencingFileSet
from variant.models import *
from gene.models import *
from body.models import *
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import json
import xlrd
import string
import random
from itertools import groupby,chain
import re
import ast
from pathlib import Path
import pandas as pd


def migrate(request):

    if request.method=="POST":
        form = MigrationForm(request.POST, request.FILES)

        if form.is_valid():

            app = form.cleaned_data["app"]

            file = form.cleaned_data["file"].read().decode('utf-8')

            report = []
            reader = csv.reader(StringIO(file))
            row = next(reader) #skip first row

            for i,col in enumerate(row):
                print("%s:%d" % (col,i))


            for row in reader:
                try:
                    if app == "project":

                        import random
                        import string

                        def get_abbreviation(name):
                            lookup = [
                                [["Acral melanoma"],"AM"],
                                [["Acral melanoma cell lines"],"AMCL"],
                                [["Nevus library","Café aul lait","lentiginous nevi"],"NL"],
                                [["Melanoma outcome study","California Registry","Melanoma prognosis"],"MOS"],
                                [["Conjunctival Melanoma"],"CONJ"],
                                [["Dysplastic nevus"],"DN"],
                                [["Progression","Melanoma evolution","Melanoma epigenetics"],"PROG"],
                                [["Dirk Hi-C"],"DHC"],
                                [["Nodular melanoma"],"NM"],
                                [["Oral melanoma"],"OM"],
                                [["Spitz melanoma"],"SM"],
                                [["Sclerotic nevi"],"SCL"],
                                [["Werner Syndrome"],"WS"],
                                [["Seattle"],""],
                                [["KIT"],"KIT"],
                                [["Iwei Medley","Fusion RNA","Possible TERT fusion","Seattle","Atypical Spitz Progression","PRKC fused cases","NRAS amplified","Deep Penetrating Melanoma","Clinical cases BCC","spatial gene expression","Fusion RNA"],"FUS"],
                                [["CGH Validation"],"CGH"]
                            ]

                            for l in lookup:
                                if name.lower().strip() in [x.lower() for x in l[0]]:
                                    # qs = Projects.objects.filter(abbreviation__startswith=l[1])
                                    # if qs.exists():
                                    #     return "%s-%d" % (l[1],len(qs))
                                    return l[1]

                            return ''.join(random.choices(string.digits, k=5))

                        def get_pi(name):
                            names = []

                            if "," in name:
                                names = name.split(",")
                            elif "/" in name:
                                names = name.split("/")
                            else:
                                names.append(name)

                            return Projects.IWEI if "Iwei" in names else Projects.BORIS

                        def get_technician(name):
                            names = []

                            if "," in name:
                                names = name.split(",")
                            elif "/" in name:
                                names = name.split("/")
                            else:
                                names.append(name)

                            qs = User.objects.filter(first_name__in=names)

                            return qs.first() if qs.exists() else User.objects.get(first_name="Noel")

                        def get_researcher(name):
                            names = []

                            if "," in name:
                                names = name.split(",")
                            elif "/" in name:
                                names = name.split("/")
                            else:
                                names.append(name)

                            qs = User.objects.filter(first_name__in=names)

                            return qs.first() if qs.exists() else None

                        project = Projects.objects.create(
                            name=row[1].strip(),
                            abbreviation=get_abbreviation(row[1]),
                            pi=get_pi(row[2]),
                            speedtype="",
                            description=row[0].strip(),
                            date_start=datetime.now(),
                        )

                        technician = get_technician(row[2])
                        if technician:
                            project.technician.add(technician)

                        researcher = get_researcher(row[2])
                        if researcher:
                            project.researcher.add(researcher)

                    elif app == "patient":

                        def get_sex(value):
                            return value.lower() if value and len(value)==1 else None

                        def get_race(value):
                            for x in Patients.RACE_TYPES:
                                if value.lower() == x[1].lower():
                                    return x[0]
                            return 7

                        patient = Patients.objects.create(
                            pat_id=row[0].strip(),
                            sex=get_sex(row[1].strip()),
                            race=get_race(row[3].strip()),
                            source=row[4].strip(),
                            notes=row[7].strip()
                        )
                    elif app == "block":

                        def get_patient(value):
                            try:
                                return Patients.objects.get(pat_id=value)
                            except Exception as e:
                                return None

                        def get_project(value):
                            try:
                                return Projects.objects.get(name=value)
                            except Exception as e:
                                return None

                        def get_body_site(value):
                            return None

                        def get_value(value):
                            return value if value and not value == "nan" else None

                        def get_float_value(value):
                            return float(value) if value and not value == "nan" else None

                        def get_ulceration(value):
                            if value == "TRUE":
                                return True
                            elif value == "FALSE":
                                return False
                            else:
                                return None

                        def get_notes(notes,description):
                            return "%s, Alternative Block IDs:%s" % (notes,description) if description else notes

                        def get_slides(value):
                            return int(value) if value and not value == "nan" else None

                        def get_slides_left(value):
                            return int(value) if value and not value == "nan" else None

                        def get_collection(value):
                            for x in Blocks.COLLECTION_CHOICES:
                                if value.lower() == x[1].lower():
                                    return x[0]
                            return Blocks.SCRAPE

                        Blocks.objects.create(
                            name=row[0].strip(),
                            patient=get_patient(row[1].strip()),
                            scan_number=get_value(row[2].strip()),
                            body_site=get_body_site(row[3].strip()),
                            ulceration=get_ulceration(row[4].strip()),
                            slides=get_value(row[5]),
                            slides_left=get_value(row[6]),
                            fixation=get_value(row[7].strip()),
                            collection=get_collection(row[8].strip()),
                            project=get_project(row[10].strip()),
                            diagnosis=get_value(row[11].strip()),
                            notes="Notes:%s;Description:%s" % (get_value(row[14].strip()),get_value(row[12].strip())),
                        )
                    elif app == "area":

                        def get_block(value):
                            try:
                                return Blocks.objects.get(name=value)
                            except Exception as e:
                                None

                        def get_collection(value):
                            for x in Blocks.COLLECTION_CHOICES:
                                if value.lower() == x[1].lower():
                                    return x[0]
                            return Blocks.SCRAPE

                        def get_area_type(value):
                            for x in Areas.AREA_TYPE_TYPES:
                                if value.lower() == x[1].lower():
                                    return x[0]
                            return None

                        def get_completion_date(value):
                            return datetime.strptime(value,'%m/%d/%Y') if value else datetime.now()

                        Areas.objects.create(
                            name=row[0].strip(),
                            block=get_block(row[2].strip("\"\n\ ")),
                            area_type=get_area_type(row[4]),
                            completion_date=get_completion_date(row[7]),
                            notes=row[9],
                        )

                        Blocks.objects.filter(name=row[2].strip("\"\n\ ")).update(collection=get_collection(row[3]))
                    elif app == "na":

                        def get_na_type(value):
                            for x in NucAcids.NA_TYPES:
                                if value.lower() == x[1].lower():
                                    return x[0]
                            return None

                        def get_area(value):
                            try:
                                return Areas.objects.get(name=value)
                            except Exception as e:
                                return None

                        def get_or_create_method(value):
                            if value:
                                obj,created = Method.objects.get_or_create(
                                    name=value
                                )
                                return obj
                            return None

                        def get_date(value):
                            return datetime.strptime(value,'%m/%d/%Y') if value else datetime.now()

                        def get_notes(notes,re_ext,total_ext,na_shared,shear_vol,te):
                            result = notes
                            if re_ext:
                                result += "Re-extraction amount:%s;" % re_ext
                            if total_ext:
                                result += "Total extracted NA amount (ng):%s;" % total_ext
                            if na_shared:
                                result += "NA sheared/used (ng):%s;" % na_shared
                            if shear_vol:
                                result += "Shearing volume DNA input (ul):%s;" % shear_vol
                            if te:
                                result += "Volume of TE buffer (ul)  for shearing:%s;" % te

                            return result

                        def get_float_value(value):
                            return float(value) if value else 0

                        NucAcids.objects.create(
                            name=row[0].strip(),
                            area=get_area(row[1].strip()),
                            na_type=get_na_type(row[2].strip()),
                            date=get_date(row[3].strip()),
                            method=get_or_create_method(row[4].strip()),
                            conc=get_float_value(row[5]),
                            vol_init=get_float_value(row[6]),
                            notes=get_notes(row[14],row[8],row[9],row[10],row[11],row[12]),
                        )
                    elif app == "sl":

                        def get_barcode(value):
                            return Barcode.objects.get(barcode_set__active=True,name=value) if value else Barcode.objects.filter(barcode_set__active=True).first()

                        def get_or_create_bait(value):
                            if value:
                                obj,created = Bait.objects.get_or_create(
                                    name=value
                                )
                                return obj
                            return None

                        def create_na_sl_link(sl,value,lp_dna,qPCR):
                            try:
                                vol = round(lp_dna/qPCR,2)
                            except Exception as e:
                                vol = 0

                            if value:
                                for na in value.split(","):
                                    NA_SL_LINK.objects.create(
                                        nucacid=NucAcids.objects.filter(name=na).first(),
                                        sample_lib=sl,
                                        input_vol=vol,
                                        # input_amount=0
                                    )

                        def create_cl(name,bait,frag_size,amp_cycle):
                            try:
                                return CapturedLib.objects.get(name=name)
                            except Exception as e:
                                return CapturedLib.objects.create(
                                    name=name,
                                    bait=get_or_create_bait(bait),
                                    frag_size=frag_size if frag_size else 0,
                                    amp_cycle=amp_cycle if amp_cycle else 0
                                )

                        def create_sl_cl_link(sl,cl,lp_dna,qPCR):
                            try:
                                vol = round(lp_dna/qPCR,2)
                            except Exception as e:
                                vol = 0

                            SL_CL_LINK.objects.create(
                                captured_lib=cl,
                                sample_lib=sl,
                                volume=vol
                            )

                        def get_date(value):
                            return datetime.strptime(value,'%m/%d/%Y') if value else datetime.now()

                        def get_float_value(value):
                            return float(value) if value else 0

                        sl = SampleLib.objects.create(
                            name=row[0].strip(),
                            barcode=get_barcode(row[22].strip()),
                            date=get_date(row[23]),
                            qpcr_conc=get_float_value(row[8]),
                            amount_final=get_float_value(row[13]),
                            vol_init=get_float_value(row[9]),
                            notes=row[24],
                        )

                        create_na_sl_link(sl,row[1],row[10],row[8])

                        for item in row[16].split(","):
                            cl = create_cl(item.strip(),row[20].strip(),row[14],row[19])

                            create_sl_cl_link(sl,cl,row[10],row[8])
                    elif app == "cl":

                        def get_date(value):
                            return datetime.strptime(value,'%m/%d/%Y') if value else datetime.now()

                        def get_sequencer(value):
                            if value:
                                arr = value.split(" ")
                                value = "%s %s" % (arr[0],arr[1])
                                for x in SequencingRun.SEQUENCER_TYPES:
                                    if value.lower() in x[1].lower():
                                        return x[0]
                            return None

                        def get_pe(value):
                            if "PE100" in value:
                                return SequencingRun.PE_TYPES[0][0]
                            elif "PE150" in value:
                                return SequencingRun.PE_TYPES[1][0]
                            return None

                        def get_or_create_sequencinglib(name,date):
                            try:
                                return SequencingLib.objects.get(name=name)
                            except ObjectDoesNotExist as e:
                                return SequencingLib.objects.create(
                                    name = name,
                                    date = date,
                                    notes = "related with sequencing run",
                                )

                        def get_capturedlib(value):
                            return CapturedLib.objects.get(name=value)

                        def create_cl_seql_link(cl,seq_l):
                            CL_SEQL_LINK.objects.create(
                                captured_lib = cl,
                                sequencing_lib = seq_l
                            )

                        for item in row[1].replace(";",",").split(","):
                            seq_l = get_or_create_sequencinglib(item.strip(),get_date(row[2]))
                            cl = get_capturedlib(row[0].strip())

                            create_cl_seql_link(cl,seq_l)

                            if not SequencingRun.objects.filter(name = item.strip()).exists():
                                sequencing_run = SequencingRun.objects.create(
                                    name = item.strip(),
                                    date = get_date(row[2]),
                                    facility = row[3].strip(),
                                    sequencer = get_sequencer(row[4].strip()),
                                    pe = get_pe(row[4].strip()),
                                    notes = row[9]
                                )

                                sequencing_run.sequencing_libs.add(seq_l)
                    elif app == "old_barcode":
                        Barcode.objects.create(
                            barcode_set=Barcodeset.objects.get(name="Old Barcodes"),
                            name=row[0],
                            i5=row[3],
                            i7=row[2]
                        )
                    elif app == "new_barcode":
                        Barcode.objects.create(
                            barcode_set=Barcodeset.objects.get(name="New Barcodes"),
                            name=row[0],
                            i5=row[3],
                            i7=row[2]
                        )
                    elif app == "sf":

                        def get_sample_lib(value):
                            try:
                                return SampleLib.objects.get(name=value)
                            except Exception as e:
                                return None

                        r1_files = row[2].split(";")
                        r1_checksums = row[3].split(";")
                        r1_counts = row[4].split(";")
                        r2_files = row[5].split(";")
                        r2_checksums = row[6].split(";")
                        r2_counts = row[7].split(";")
                        for i in range(len(r1_files)):
                            sf = SequencingFile.objects.create(
                                sample_lib=get_sample_lib(row[0].strip()),
                                folder_name=row[1].strip(),
                                read1_file=r1_files[i].strip(),
                                read1_checksum=r1_checksums[i].strip(),
                                read1_count=r1_counts[i].strip(),
                                read2_file=r2_files[i].strip(),
                                read2_checksum=r2_checksums[i].strip(),
                                read2_count=r2_counts[i].strip(),
                                is_read_count_equal=True if row[8].strip() == "Yes" else False ,
                                path=row[9].strip(),
                            )
                    elif app == "md5":
                        for i,sub in enumerate(row[2].split(";")):
                            SequencingFile.objects.create(
                                sample_lib = SampleLib.objects.get_or_create(name=row[0].strip())[0],
                                folder_name = row[1].strip(),
                                read1_file = sub,
                                read1_checksum = row[3].split(";")[i],
                                read1_count = row[4].split(";")[i],
                                read2_file = row[5].split(";")[i],
                                read2_checksum = row[6].split(";")[i],
                                read2_count = row[7].split(";")[i],
                                is_read_count_equal = True if row[8].strip() == "Yes" else False,
                                path = row[9].strip(),
                            )

                    print("migrated..")
                    report.append({"name":row[0],"status":"OK","message":""})
                except Exception as e:
                    print(str(e))
                    print(row)
                    report.append({"name":row[0],"status":"FAILED","message":str(e)})

            print("Process completed successfully")

            response = HttpResponse(
                content_type='text/csv',
                headers={'Content-Disposition': 'attachment; filename="report-%s.csv"' % app},
            )

            field_names = ["name","status","message"]
            writer = csv.writer(response)
            writer.writerow(field_names)
            for item in report:
                writer.writerow([item[field] for field in field_names])

            return response

        else:
            print("Process could not be completed!")
    else:
        form = MigrationForm()

    return render(request,"migration.html",locals())

def report(request):
    import csv
    from io import StringIO

    result = []

    class Report():
        patient = None
        block = None
        area = None
        nucacid = None
        sample_lib = None
        captured_lib = None
        bait = None
        sequencing_lib = None
        sequencing_run = None
        fastq_file = None
        path = None
        na_type = None
        area_type = None
        matching_normal_sl = None

    for sample_lib in SampleLib.objects.all():

        report = Report()

        fastq_files = {}
        md5_checksums = []
        paths = []

        for x in sample_lib.sequencing_files.all():
            fastq_files.update({x.read1_file:x.read1_checksum})
            paths.append(x.path)

        report.sample_lib = sample_lib.name
        report.fastq_file = fastq_files
        report.path = ",".join(list(set(paths)))

        # from sample_lib to nucleic_acid..->project
        for na_sl_link in sample_lib.na_sl_links.all():
            report.na_type = na_sl_link.nucacid.get_na_type_display() if na_sl_link.nucacid else None
            report.area_type = na_sl_link.nucacid.area.get_area_type_display() if na_sl_link.nucacid.area and na_sl_link.nucacid.area.area_type else None
            report.nucacid = na_sl_link.nucacid if na_sl_link else None
            report.area = na_sl_link.nucacid.area.name if na_sl_link.nucacid.area else None
            report.block = na_sl_link.nucacid.area.block if na_sl_link.nucacid and na_sl_link.nucacid.area else None
            report.patient = na_sl_link.nucacid.area.block.patient if na_sl_link.nucacid.area and na_sl_link.nucacid.area.block and na_sl_link.nucacid.area.block.patient else None

            if not report.area_type == "Normal":
                report.matching_normal_sl = ",".join(list(NA_SL_LINK.objects.filter(nucacid__area__block__patient=report.patient,nucacid__area__area_type__in=["normal","normal2","normal3"]).values_list("sample_lib__name",flat=True)))

        # from sample_lib to captured_lib..->sequencing_run
        for sl_cl_link in sample_lib.sl_cl_links.all():
            report.captured_lib = sl_cl_link.captured_lib.name
            report.bait = sl_cl_link.captured_lib.bait

            for cl_seql_link in sl_cl_link.captured_lib.cl_seql_links.all():
                report.sequencing_lib = cl_seql_link.sequencing_lib.name
                for sequencing_run in cl_seql_link.sequencing_lib.sequencing_runs.all():
                    report.sequencing_run = sequencing_run.name


        NA_SL_LINK.objects.filter(nucacid__area__block__patient=report.patient).exclude(nucacid__area__area_type__in=["normal","normal2","normal3"]).values_list("sample_lib__name",flat=True)

        result.append(report)

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="report-consolidated_data-v5.csv"'},
    )

    field_names = ["patient","block","area","nucacid","sample_lib","captured_lib","bait","sequencing_lib","sequencing_run","fastq_file","path","na_type","area_type","matching_normal_sl"]
    writer = csv.writer(response)
    writer.writerow(field_names)
    for item in result:
        writer.writerow([getattr(item,field) for field in field_names])

    return response

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

def consolidated_data_old(request):
    tree2_dataset = []
    checksum_dataset = None
    result = []
    old_pat_ids = []

    def get_value(value):
        if str(value).replace(".", "").isnumeric():
            return str(int(value))
        else:
            return value

    def _simplify_tree2(f):
        while True:
            line = f.readline().decode("utf-8").strip()
            if not line:
                break
            if "fastq.gz" in line:
                tree2_dataset.append(line)

    def _simplify_old_pat_id(f):
        xl_workbook = xlrd.open_workbook(file_contents=f.read())
        sheet_names = xl_workbook.sheet_names()
        xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])
        for i in range(0,xl_sheet.nrows):
            old_pat_ids.append((xl_sheet.row(i)[0].value,xl_sheet.row(i)[19].value))

    def _get_checksum(sl_id,filename):
        for c in checksum_dataset:
            if c["sl_id"] == sl_id and c["filename"] == filename:
                return c["checksum"]
        return None

    def __search_in_tree2(sl_id,seq_r):
        files = []
        for line in tree2_dataset:
            if sl_id in line:
                parts = line.split("/")
                if seq_r.name in parts[1]:
                    files.append({
                        "fastq_file": parts[-1],
                        "directory": parts[1],
                        "path": line,
                        "checksum": _get_checksum(sl_id,parts[-1])
                    })
        return files

    def __search_in_pat_id(value):
        for p in old_pat_ids:
            if p[0] == value:
                return p[1]
        return None

    def get_barcode(name):
        try:
            return Barcode.objects.get(name=name)
        except Exception as e:
            return Barcode.objects.get(name="Unknown")

    def get_or_create_na_sl_link(sl,na):
        try:
            return NA_SL_LINK.objects.get(
                nucacid=na,
                sample_lib=sl
            )
        except Exception as e:
            return NA_SL_LINK.objects.create(
                nucacid=na,
                sample_lib=sl
            )

    def get_or_create_sl_cl_link(sl,cl):
        try:
            return SL_CL_LINK.objects.get(
                captured_lib=cl,
                sample_lib=sl
            )
        except Exception as e:
            return SL_CL_LINK.objects.create(
                captured_lib=cl,
                sample_lib=sl
            )

    def get_or_create_cl_seql_link(cl,seq_l):
        try:
            return CL_SEQL_LINK.objects.get(
                captured_lib = cl,
                sequencing_lib = seq_l
            )
        except Exception as e:
            return CL_SEQL_LINK.objects.create(
                captured_lib = cl,
                sequencing_lib = seq_l
            )

    def get_or_create_bait(value):
        try:
            return Bait.objects.get(name=value)
        except Exception as e:
            if not value:
                return None
            return Bait.objects.create(
                name=value
            )

    def get_or_create_capturedlib(name,bait):
        try:
            return CapturedLib.objects.get(name=name)
        except Exception as e:
            return CapturedLib.objects.create(
                name=name,
                bait=bait,
            )

    def get_or_create_samplelib(**kwargs):
        try:
            return SampleLib.objects.get(name=kwargs["name"])
        except ObjectDoesNotExist as e:
            return SampleLib.objects.create(**kwargs)

    def get_or_create_sequencingrun(name):
        try:
            return SequencingRun.objects.get(name=name)
        except ObjectDoesNotExist as e:
            return SequencingRun.objects.create(
                name = name,
            )

    def get_or_create_sequencinglib(name):
        try:
            return SequencingLib.objects.get(name=name)
        except ObjectDoesNotExist as e:
            return SequencingLib.objects.create(
                name = name,
            )

    def get_or_create_sequencingfile(**kwargs):
        try:
            return SequencingFile.objects.get_or_create(**kwargs)[0]
        except Exception as e:
            return None

    def get_or_create_patient(**kwargs):
        try:
            return Patients.objects.get(pat_id=kwargs["pat_id"])
        except ObjectDoesNotExist as e:
            return Patients.objects.create(**kwargs)

    def get_or_create_block(**kwargs):
        try:
            return Blocks.objects.get(name=kwargs["name"])
        except ObjectDoesNotExist as e:
            return Blocks.objects.create(**kwargs)

    def get_or_create_area(**kwargs):
        try:
            return Areas.objects.get(name=kwargs["name"])
        except ObjectDoesNotExist as e:
            return Areas.objects.create(**kwargs)

    def get_or_create_nucacid(**kwargs):
        try:
            return NucAcids.objects.get(name=kwargs["name"])
        except ObjectDoesNotExist as e:
            return NucAcids.objects.create(**kwargs)

    def __get_random_string():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    def __get_area_type_by_block(group):
        if not type(group) == list:
            group = [group]
        return any([xl_sheet.row(i)[13].value.strip()=="Normal" for i in range(0,xl_sheet.nrows) for g in group if g == xl_sheet.row(i)[1].value.strip()])

    def __get_pat_id(group):
        result = None
        if not type(group) == list:
            group = [group]
        for g in group:
            result = __search_in_pat_id(g)
            break
        return result if result else __get_random_string()

    def _generate_pat_id_by_block(xl_sheet):
        pattern = "^[A-Z]+\-\d+\-\d+|^[A-Z]+\d+\-\d{2,6}|^HW[0-9]\-|^HW Acral #[0-9]+\s|^[A-Z]+\_[0-9]+\_|^[0-9]{2}\-[0-9]{5}"

        blocks = [xl_sheet.row(i)[1].value.strip() for i in range(0,xl_sheet.nrows) if not xl_sheet.row(i)[27].value and not xl_sheet.row(i)[1].value == "nan"]

        def projection(val):
            x = re.findall(pattern,val)
            return x[0] if x else random.randint(0,9999999999999)

        x_sorted = sorted(blocks) # sort the data
        x_grouped_for_equals = list([x for x in [list(it) for k, it in groupby(x_sorted)] if len(x)>1]) #the group of the records with same block id

        blocks = [x for x in blocks if x not in list(chain(*x_grouped_for_equals))] #remove from list the found ones

        x_sorted = sorted(blocks) # sort again
        x_grouped_for_similars = list([x for x in [list(it) for k, it in groupby(x_sorted,projection)] if len(x)>1]) #the group of the records with similar block id

        blocks = [x for x in blocks if x not in list(chain(*x_grouped_for_similars))] #remove from list the found ones

        result = x_grouped_for_equals + x_grouped_for_similars + blocks

        return [(x,__get_pat_id(x), __get_area_type_by_block(x)) for x in result]

    def _generate_pat_id_by_sample_lib(xl_sheet):
        pattern="^[A-Z]+\_\d+|^[A-Z]+\d+\_|^[A-Z][A-Z]\_|^[A-Za-z]+\s\d+|^[A-Za-z]+\_\d+|^[A-Za-z]+\-[A-Z0-9]+\-|[0-9]+\_"

        sample_libs = [xl_sheet.row(i)[0].value.strip() for i in range(0,xl_sheet.nrows) if not xl_sheet.row(i)[27].value and xl_sheet.row(i)[1].value == "nan"]

        def projection(val):
            x = re.findall(pattern,val)
            return x[0] if x else random.randint(0,9999999999999)

        x_sorted = sorted(sample_libs) # sort the data
        x_grouped = list([x for x in [list(it) for k, it in groupby(x_sorted)] if len(x)>1])

        single_sample_libs = [x for x in sample_libs if x not in list(chain(*x_grouped))] #remove from list the found ones

        result = x_grouped + sample_libs

        return [(x,__get_random_string()) for x in enumerate(result)]

    if request.method == "POST":
        form = ConsolidatedDataForm(request.POST, request.FILES)

        if form.is_valid():
            consolidated_data_file = request.FILES["consolidated_data_file"]
            # md5_summary_file = request.FILES["md5_summary_file"]
            tree2_file = request.FILES["tree2_file"]
            checksum_dataset = json.loads(request.FILES["checksum_dataset"].read())
            # pat_id_file = request.FILES["old_pat_id_file"]

            # xl_workbook = xlrd.open_workbook(file_contents=consolidated_data_file.read())
            # sheet_names = xl_workbook.sheet_names()
            # xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])

            # for i in range(0,xl_sheet.ncols):
            #     row = xl_sheet.row(0)
            #     print("%d: %s" % (i,row[i].value))

            _simplify_tree2(tree2_file)

            # _simplify_old_pat_id(pat_id_file)

            xl_workbook = xlrd.open_workbook(file_contents=consolidated_data_file.read())
            sheet_names = xl_workbook.sheet_names()
            xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])

            # generated_pat_ids_by_block = _generate_pat_id_by_block(xl_sheet)

            # generated_pat_ids_by_sample_lib = _generate_pat_id_by_sample_lib(xl_sheet)

            for i in range(1,xl_sheet.nrows):
                try:
                    report = {}
                    row = xl_sheet.row(i)

                    patient = get_or_create_patient(**{"pat_id":get_value(row[29].value), "sex":row[22].value.lower() if row[22].value else None})

                    block = get_or_create_block(**{"name":get_value(row[1].value),"patient":patient,"age":int(row[23].value) if row[23].value else None,"diagnosis":row[7].value,"micro":row[21],"p_stage":row[24].value,"thickness":float(row[25].value) if row[25].value else None,"subtype":row[26].value,"prim":row[27].value,"mitoses":int(row[28].value) if row[28].value else None,"ip_dx":row[18].value,"notes":row[8].value})

                    area = get_or_create_area(**{"name":row[14].value,"block":block, "area_type": "other" if row[12].value and row[12].value=="Tumor" else row[12].value.lower() })

                    nucacid = get_or_create_nucacid(**{"name":row[15].value,"area":area})

                    barcode = get_barcode(row[2].value.strip() if not isinstance(row[2].value,float) else int(row[2].value))

                    amount_in = 0
                    if row[5].value and not isinstance(row[5].value, float):
                        parts = row[5].value.split(" ")
                        if parts[1] == "ug":
                            amount_in = float(parts[0]) * 1000
                        elif parts[1] == "ng":
                            amount_in = float(parts[0])

                    sample_lib = get_or_create_samplelib(**{"name":get_value(row[0].value),"barcode":barcode,"amount_in":amount_in,"notes":"Notes:%s, Condition:%s, Input Hyb Conc.:%s" % (row[20].value, row[4].value, row[6].value)})

                    na_sl_link = get_or_create_na_sl_link(sample_lib,nucacid)

                    bait = get_or_create_bait(row[13].value)

                    captured_lib = get_or_create_capturedlib(row[11].value,bait)

                    sl_cl_link = get_or_create_sl_cl_link(sample_lib,captured_lib)

                    sequencing_lib = get_or_create_sequencinglib(row[9].value.split("_")[1])

                    cl_seql_link = get_or_create_cl_seql_link(captured_lib,sequencing_lib)

                    sequencing_run = get_or_create_sequencingrun(row[9].value.split("_")[1])

                    sequencing_run.sequencing_libs.add(sequencing_lib)

                    fastq_files = __search_in_tree2(str(row[0].value),sequencing_run)

                    for f in fastq_files:
                        sequencing_file = get_or_create_sequencingfile(**{
                            "sample_lib":sample_lib,
                            "folder_name":f["directory"],
                            "read1_file":f["fastq_file"],
                            "read1_checksum":f["checksum"],
                            "path":f["path"]
                        })

                    result.append(report)
                except Exception as e:
                    pass

            # response = HttpResponse(
            #     content_type='text/csv',
            #     headers={'Content-Disposition': 'attachment; filename="report-consolidated_data.csv"'},
            # )
            #
            # field_names = list(result[0].keys())
            # writer = csv.writer(response)
            # writer.writerow(field_names)
            # for item in result:
            #     writer.writerow([item[field] for field in field_names])
            #
            # return response

    else:
        form = ConsolidatedDataForm()
    return render(request, "consolidated_data.html", locals())

def lookup_all_data(request):
    result = []
    tree2_dataset = []
    checksum_dataset = None

    class Report:
        sample_lib = None
        nucleic_acid = None
        area = None
        block = None
        # patient = None
        sequencing_run = None
        sequencing_lib = None
        captured_lib = None
        bait = None
        spike = None
        source = None
        directory = None
        fastq_file = None
        checksum = None
        path = None

        def __init__(self,source):
            self.source = source

    def __search_in_database(value):
        try:
            sequencing_run = SequencingRun.objects.get(name=value)
            for seq_l in sequencing_run.sequencing_libs.all():
                for cl_seql_link in seq_l.cl_seql_links.all():
                    for sl_cl_link in cl_seql_link.captured_lib.sl_cl_links.all():
                        sample_lib = sl_cl_link.sample_lib
                        captured_lib = sl_cl_link.captured_lib
                        for na_sl_link in sample_lib.na_sl_links.all():
                            nucacid = na_sl_link.nucacid
                            return {
                                "sample_lib": sample_lib.name,
                                "nucleic_acid": nucacid.name,
                                "area": nucacid.area.name if nucacid.area else None,
                                "block": nucacid.area.block.name if nucacid.area and nucacid.area.block else None,
                                # "patient": nucacid.area.block.patient.pat_id if nucacid.area and nucacid.area.block and nucacid.area.block.patient else None,
                                "captured_lib": captured_lib,
                                "sequencing_lib": seq_l,
                                "bait": captured_lib.bait.name if captured_lib.bait else None
                            }

        except Exception as e:
            return None

    def _simplify_tree2(f):
        while True:
            line = f.readline().decode("utf-8").strip()
            if not line:
                break
            if "fastq.gz" in line:
                tree2_dataset.append(line)

    def __search_in_tree2(sl_id,sequencing_run):
        for line in tree2_dataset:
            if value in line:
                parts = line.split("/")
                return {
                    "fastq_file": parts[-1],
                    "directory": parts[1],
                    "path": line
                }
        return None

    def _run_consolidated_data(f):
        xl_workbook = xlrd.open_workbook(file_contents=f.read())
        sheet_names = xl_workbook.sheet_names()
        xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])

        for i in range(1,xl_sheet.nrows):
            row = xl_sheet.row(i)

            report = Report(source="consolidated_data")
            report.sample_lib = row[0].value
            report.block = row[1].value
            report.sequencing_run = row[11].value.split("_")[-1]
            report.nucleic_acid = row[12].value if not row[12].value == "nan_NA" else None
            report.area = row[15].value
            report.sequencing_lib = row[13].value
            report.captured_lib = row[14].value
            report.bait = row[9].value
            report.spike = row[10].value
            report.checksum = _get_checksum(row[0].value)

            tree2_values = __search_in_tree2(str(row[0].value))

            if tree2_values:
                report.fastq_file = tree2_values["fastq_file"]
                report.directory = tree2_values["directory"]
                report.path = tree2_values["path"]


            result.append(report)

    def _run_consolidated_matched_data(f):
        xl_workbook = xlrd.open_workbook(file_contents=f.read())
        sheet_names = xl_workbook.sheet_names()
        xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])

        for i in range(1,xl_sheet.nrows):
            row = xl_sheet.row(i)

            report = Report(source="consolidated_data")
            report.sample_lib = row[0].value
            report.block = row[1].value  if not row[1].value == "nan" else None
            report.sequencing_run = row[9].value.split("_")[-1]
            report.nucleic_acid = row[10].value
            report.area = row[13].value
            report.sequencing_lib = row[11].value
            report.captured_lib = row[12].value
            report.bait = row[14].value
            report.checksum = _get_checksum(row[0].value)

            tree2_values = __search_in_tree2(str(row[0].value))

            if tree2_values:
                report.fastq_file = tree2_values["fastq_file"]
                report.directory = tree2_values["directory"]
                report.path = tree2_values["path"]


            result.append(report)

    def _run_md5_summary(f):
        xl_workbook = xlrd.open_workbook(file_contents=f.read())
        sheet_names = xl_workbook.sheet_names()
        xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])

        for i in range(1,xl_sheet.nrows):
            row = xl_sheet.row(i)

            report = Report(source="md5_summary")
            report.sample_lib = row[0].value
            report.sequencing_run = row[1].value.strip().split("_")[-1] if "_" in row[1].value and not row[1].value in ["Acral_melenoma_lines_mRNA_Seq_AL1806051_R1","Acral_Mel_Exome-01","BCB018_Part1","BCB018_Part2",] else row[1].value.strip()
            report.checksum = _get_checksum(row[0].value)

            tree2_values = __search_in_tree2(row[0].value)

            if tree2_values:
                report.fastq_file = tree2_values["fastq_file"]

                db_values = __search_in_database(row[1].value.strip())

                if db_values:
                    report.sample_lib = db_values["sample_lib"]
                    report.nucleic_acid = db_values["nucleic_acid"]
                    report.area= db_values["area"]
                    report.block = db_values["block"]
                    report.captured_lib = db_values["captured_lib"]
                    report.sequencing_lib = db_values["sequencing_lib"]
                    report.bait = db_values["bait"]


            result.append(report)

    def _get_checksum(value):
        for c in checksum_dataset:
            if c["sl_id"] == value:
                return c["checksum"]
        return None

    if request.method == "POST":
        form = LookupAllDataForm(request.POST, request.FILES)

        if form.is_valid():
            consolidated_data_file = request.FILES["consolidated_data_file"]
            md5_summary_file = request.FILES["md5_summary_file"]
            tree2_file = request.FILES["tree2_file"]
            checksum_dataset = json.loads(request.FILES["checksum_dataset"].read())

            _simplify_tree2(tree2_file)

            # _run_consolidated_data(consolidated_data_file)
            _run_consolidated_matched_data(consolidated_data_file)

            _run_md5_summary(md5_summary_file)

            response = HttpResponse(
                content_type='text/csv',
                headers={'Content-Disposition': 'attachment; filename="report-seq-files-v4.csv"'},
            )

            field_names = ["sample_lib","nucleic_acid","area","block","captured_lib","sequencing_lib","sequencing_run","bait","directory","checksum","fastq_file","path","source"]
            writer = csv.writer(response)
            writer.writerow(field_names)

            for item in result:
                writer.writerow([getattr(item,field) for field in field_names])

            return response
    else:
        form = LookupAllDataForm()

    return render(request,"lookup.html",locals())

def consolidated_data(request):

    consolidated_data = []
    md5_summary = []
    x1 = 0
    x2 = 0

    def get_value(value):
        if str(value).replace(".", "").isnumeric():
            return str(int(value))
        else:
            return value

    def get_barcode(name):
        try:
            return Barcode.objects.get(name=name)
        except Exception as e:
            return Barcode.objects.get(name="Unknown")

    def get_or_create_na_sl_link(sl,na):
        try:
            return NA_SL_LINK.objects.get(
                nucacid=na,
                sample_lib=sl
            )
        except Exception as e:
            return NA_SL_LINK.objects.create(
                nucacid=na,
                sample_lib=sl
            )

    def get_or_create_sl_cl_link(sl,cl):
        try:
            return SL_CL_LINK.objects.get(
                captured_lib=cl,
                sample_lib=sl
            )
        except Exception as e:
            return SL_CL_LINK.objects.create(
                captured_lib=cl,
                sample_lib=sl
            )

    def get_or_create_cl_seql_link(cl,seq_l):
        try:
            return CL_SEQL_LINK.objects.get(
                captured_lib = cl,
                sequencing_lib = seq_l
            )
        except Exception as e:
            return CL_SEQL_LINK.objects.create(
                captured_lib = cl,
                sequencing_lib = seq_l
            )

    def get_or_create_bait(value):
        try:
            return Bait.objects.get(name=value)
        except Exception as e:
            if not value:
                return None
            return Bait.objects.create(
                name=value
            )

    def get_or_create_capturedlib(name,bait):
        try:
            return CapturedLib.objects.get(name=name)
        except Exception as e:
            return CapturedLib.objects.create(
                name=name,
                bait=bait,
            )

    def get_or_create_samplelib(**kwargs):
        try:
            return SampleLib.objects.get(name=kwargs["name"])
        except ObjectDoesNotExist as e:
            return SampleLib.objects.create(**kwargs)

    def get_or_create_sequencingrun(name):
        try:
            return SequencingRun.objects.get(name=name)
        except ObjectDoesNotExist as e:
            return SequencingRun.objects.create(
                name = name,
            )

    def get_or_create_sequencinglib(name):
        try:
            return SequencingLib.objects.get(name=name)
        except ObjectDoesNotExist as e:
            return SequencingLib.objects.create(
                name = name,
            )

    def get_or_create_sequencingfile(**kwargs):
        try:
            return SequencingFile.objects.get_or_create(**kwargs)[0]
        except Exception as e:
            return None

    def get_or_create_patient(**kwargs):
        try:
            return Patients.objects.get(pat_id=kwargs["pat_id"])
        except ObjectDoesNotExist as e:
            return Patients.objects.create(**kwargs)

    def get_or_create_block(**kwargs):
        try:
            return Blocks.objects.get(name=kwargs["name"])
        except ObjectDoesNotExist as e:
            return Blocks.objects.create(**kwargs)

    def get_or_create_area(**kwargs):
        try:
            return Areas.objects.get(name=kwargs["name"])
        except ObjectDoesNotExist as e:
            return Areas.objects.create(**kwargs)

    def get_or_create_nucacid(**kwargs):
        try:
            return NucAcids.objects.get(name=kwargs["name"])
        except ObjectDoesNotExist as e:
            return NucAcids.objects.create(**kwargs)

    def initialize_consolidated_data(f):
        xl_workbook = xlrd.open_workbook(file_contents=f.read())
        sheet_names = xl_workbook.sheet_names()
        xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])
        return [[xl_sheet.row(i)[j].value for j in range(0,xl_sheet.ncols)] for i in range(1,xl_sheet.nrows)]

    def initialize_md5_summary(f):
        xl_workbook = xlrd.open_workbook(file_contents=f.read())
        sheet_names = xl_workbook.sheet_names()
        xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])
        return [[xl_sheet.row(i)[j].value for j in range(0,xl_sheet.ncols)] for i in range(1,xl_sheet.nrows)]

    added = []
    def get_fastq_files_by_sequencing_run(md5_summary,seq_r):
        result = []
        for m in md5_summary:
            if m[1] == seq_r and m[1] not in added:
                read1_files = list(zip(m[2].split(";"),m[3].split(";")))
                read2_files = list(zip(m[5].split(";"),m[6].split(";")))
                for i in range(0,len(read1_files)):
                    result.append({
                        "folder_name":m[0],
                        "read1_file":read1_files[i][0],
                        "read1_checksum":read1_files[i][1],
                        "read2_file":read2_files[i][0],
                        "read2_checksum":read2_files[i][1],
                        "is_read_count_equal": True if row[8].strip() == "Yes" else False,
                        "path":m[9]
                    })
                added.append(seq_r)

        return result

    def get_fastq_files_by_sample_lib(md5_summary,sample_lib, sequencing_run):
        result = []
        for m in md5_summary:
            if str(sample_lib) in str(m[0]) and m[1] == sequencing_run:
                read1_files = list(zip(m[2].split(";"),m[3].split(";")))
                read2_files = list(zip(m[5].split(";"),m[6].split(";")))
                for i in range(0,len(read1_files)):
                    result.append({
                        "folder_name":m[0],
                        "read1_file":read1_files[i][0],
                        "read1_checksum":read1_files[i][1],
                        "read1_count":m[4],
                        "read2_file":read2_files[i][0],
                        "read2_checksum":read2_files[i][1],
                        "read2_count":m[7],
                        "is_read_count_equal": True if m[8].strip() == "Yes" else False,
                        "path":m[9]
                    })
        return result

    if request.method == "POST":
        form = ConsolidatedDataForm(request.POST, request.FILES)

        if form.is_valid():
            consolidated_data_file = request.FILES["consolidated_data_file"]
            md5_summary_file = request.FILES["md5_summary_file"]

            # for i in range(0,xl_sheet.ncols):
            #     row = xl_sheet.row(0)
            #     print("%d: %s" % (i,row[i].value))
            md5_summary = initialize_md5_summary(md5_summary_file)

            consolidated_data = initialize_consolidated_data(consolidated_data_file)

            for row in consolidated_data:
                try:
                    patient = get_or_create_patient(**{"pat_id":get_value(row[29]), "sex":row[22].lower() if row[22] else None})

                    block = get_or_create_block(**{"name":get_value(row[1]),"patient":patient,"age":int(row[23]) if row[23] else None,"diagnosis":row[7],"micro":row[21],"p_stage":row[24],"thickness":float(row[25]) if row[25] else None,"subtype":row[26],"prim":row[27],"mitoses":int(row[28]) if row[28] else None,"ip_dx":row[18],"notes":row[8]})

                    area = get_or_create_area(**{"name":row[14],"block":block, "area_type": "other" if row[12] and row[12]=="Tumor" else row[12].lower() })

                    nucacid = get_or_create_nucacid(**{"name":row[15],"area":area})

                    barcode = get_barcode(row[2].strip() if not isinstance(row[2],float) else int(row[2]))

                    amount_in = 0
                    if row[5] and not isinstance(row[5], float):
                        parts = row[5].split(" ")
                        if parts[1] == "ug":
                            amount_in = float(parts[0]) * 1000
                        elif parts[1] == "ng":
                            amount_in = float(parts[0])

                    sample_lib = get_or_create_samplelib(**{"name":get_value(row[0]),"barcode":barcode,"amount_in":amount_in,"notes":"Notes:%s, Condition:%s, Input Hyb Conc.:%s" % (row[20], row[4], row[6])})

                    na_sl_link = get_or_create_na_sl_link(sample_lib,nucacid)

                    bait = get_or_create_bait(row[13])

                    captured_lib = get_or_create_capturedlib(row[11],bait)

                    sl_cl_link = get_or_create_sl_cl_link(sample_lib,captured_lib)

                    sequencing_lib = get_or_create_sequencinglib(row[9].split("_")[1])

                    cl_seql_link = get_or_create_cl_seql_link(captured_lib,sequencing_lib)

                    sequencing_run = get_or_create_sequencingrun(row[9].split("_")[1])

                    sequencing_run.sequencing_libs.add(sequencing_lib)

                    fastq_files = get_fastq_files_by_sample_lib(md5_summary,row[0],row[9])

                    for f in fastq_files:
                        sequencing_file = get_or_create_sequencingfile(**{
                            "sample_lib":sample_lib,
                            "folder_name":f["folder_name"],
                            "read1_file":f["read1_file"],
                            "read1_checksum":f["read1_checksum"],
                            "read2_file":f["read2_file"],
                            "read2_checksum":f["read2_checksum"],
                            "is_read_count_equal":f["is_read_count_equal"],
                            "path":f["path"]
                        })

                except Exception as e:
                    print(row)
                    print(str(e))
            # response = HttpResponse(
            #     content_type='text/csv',
            #     headers={'Content-Disposition': 'attachment; filename="report-consolidated_data.csv"'},
            # )
            #
            # field_names = list(result[0].keys())
            # writer = csv.writer(response)
            # writer.writerow(field_names)
            # for item in result:
            #     writer.writerow([item[field] for field in field_names])
            #
            # return response

    else:
        form = ConsolidatedDataForm()
    return render(request, "consolidated_data.html", locals())

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

def airtable_consolidated_data(request):

    consolidated_data = []

    def get_value(value):
        if str(value).replace(".", "").isnumeric():
            return str(int(value))
        else:
            return value

    def get_barcode(name):
        try:
            return Barcode.objects.get(name=name)
        except Exception as e:
            return Barcode.objects.get(name="Unknown")

    def get_or_create_na_sl_link(sl,na):
        try:
            return NA_SL_LINK.objects.get(
                nucacid=na,
                sample_lib=sl
            )
        except Exception as e:
            return NA_SL_LINK.objects.create(
                nucacid=na,
                sample_lib=sl
            )

    def get_or_create_sl_cl_link(sl,cl):
        try:
            return SL_CL_LINK.objects.get(
                captured_lib=cl,
                sample_lib=sl
            )
        except Exception as e:
            return SL_CL_LINK.objects.create(
                captured_lib=cl,
                sample_lib=sl
            )

    def get_or_create_cl_seql_link(cl,seq_l):
        try:
            return CL_SEQL_LINK.objects.get(
                captured_lib = cl,
                sequencing_lib = seq_l
            )
        except Exception as e:
            return CL_SEQL_LINK.objects.create(
                captured_lib = cl,
                sequencing_lib = seq_l
            )

    def get_or_create_bait(value):
        try:
            return Bait.objects.get(name=value)
        except Exception as e:
            if not value:
                return None
            return Bait.objects.create(
                name=value
            )

    def get_or_create_capturedlib(name,bait):
        try:
            return CapturedLib.objects.get(name=name)
        except Exception as e:
            return CapturedLib.objects.create(
                name=name,
                bait=bait,
            )

    def get_or_create_samplelib(**kwargs):
        try:
            return SampleLib.objects.get(name=kwargs["name"])
        except ObjectDoesNotExist as e:
            return SampleLib.objects.create(**kwargs)

    def get_or_create_sequencingrun(**kwargs):
        try:
            return SequencingRun.objects.get(name=kwargs["name"])
        except ObjectDoesNotExist as e:
            return SequencingRun.objects.create(**kwargs)

    def get_or_create_sequencinglib(name):
        try:
            return SequencingLib.objects.get(name=name)
        except ObjectDoesNotExist as e:
            return SequencingLib.objects.create(
                name = name,
            )

    def create_sequencingfile(**kwargs):
        try:
            SequencingFile.objects.create(**kwargs)
        except Exception as e:
            print(str(e))

    def get_or_create_patient(**kwargs):
        try:
            return Patients.objects.get(pat_id=kwargs["pat_id"])
        except ObjectDoesNotExist as e:
            return Patients.objects.create(**kwargs)

    def get_or_create_block(**kwargs):
        try:
            return Blocks.objects.get(name=kwargs["name"])
        except ObjectDoesNotExist as e:
            return Blocks.objects.create(**kwargs)

    def get_or_create_area(**kwargs):
        try:
            return Areas.objects.get(name=kwargs["name"])
        except ObjectDoesNotExist as e:
            return Areas.objects.create(**kwargs)

    def get_or_create_nucacid(**kwargs):
        try:
            return NucAcids.objects.get(name=kwargs["name"])
        except ObjectDoesNotExist as e:
            return NucAcids.objects.create(**kwargs)

    def get_area_type(value):
        for x in Areas.AREA_TYPE_TYPES:
            if value and value.lower() == x[1].lower():
                return x[0]
        return None

    def create_sequencingfile_for_fastq_files(sample_lib,sequencing_run,fastq_files,path):
        if fastq_files and isinstance(fastq_files, dict):
            fastq_files = fastq_files.replace("nan","None")
            for key,value in ast.literal_eval(fastq_files).items():
                create_sequencingfile(**{
                    "sample_lib":sample_lib,
                    "folder_name":sequencing_run,
                    "read1_file":key.strip() if key else None,
                    "read1_checksum":value.strip() if value else None,
                    "path":path.strip()
                })

    def create_sequencingfile_for_bam_files(sample_lib,sequencing_run,bam_files,path):
        if bam_files:
            bam_files = bam_files.replace("nan","None")
            for key,value in ast.literal_eval(bam_files).items():
                create_sequencingfile(**{
                    "sample_lib":sample_lib,
                    "folder_name":sequencing_run,
                    "read1_file":key.strip() if key else None,
                    "read1_checksum":value.strip() if value else None,
                    "path":path.strip()
                })

    def create_sequencingfile_for_bai_files(sample_lib,sequencing_run,bai_files,path):
        if bai_files:
            bai_files = bai_files.replace("nan","None")
            for key,value in ast.literal_eval(bai_files).items():
                create_sequencingfile(**{
                    "sample_lib":sample_lib,
                    "folder_name":sequencing_run,
                    "read1_file":key.strip() if key else None,
                    "read1_checksum":value.strip() if value else None,
                    "path":path.strip()
                })

    def initialize_consolidated_data(f):
        xl_workbook = xlrd.open_workbook(file_contents=f.read())
        sheet_names = xl_workbook.sheet_names()
        xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])
        # for i in range(0,xl_sheet.ncols):
        #     row = xl_sheet.row(0)
        #     print("%d: %s" % (i,row[i].value))
        return [[xl_sheet.row(i)[j].value for j in range(0,xl_sheet.ncols)] for i in range(1,xl_sheet.nrows)]

    if request.method == "POST":
        form = AirtableConsolidatedDataForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES["file"]

            consolidated_data = initialize_consolidated_data(file)

            for row in consolidated_data:
                try:
                    patient = get_or_create_patient(**{"pat_id":get_value(row[3]), "sex":row[25].lower() if row[25] else None,"notes":"number:%s,unnamed:%s,pat_id_airtable:%s" % (row[0], row[1], row[2])})

                    block = get_or_create_block(**{"name":row[4],"patient":patient,"age":int(row[26]) if row[26] else None,"micro":row[24],"p_stage":row[27],"thickness":float(row[28]) if row[28] else None,"subtype":row[29],"prim":row[30],"ip_dx":row[20],"notes":"dept_number:%s,specimen:%s,site_code:%s,icd9:%s" % (row[18],row[19],row[21],row[22])})

                    area = get_or_create_area(**{"name":row[5],"block":block, "area_type": get_area_type(row[16]) })

                    nucacid = get_or_create_nucacid(**{"name":row[6],"area":area})

                    sample_lib = get_or_create_samplelib(**{"name":get_value(row[7]),"notes":"air_table.1:%s" % row[8]})

                    na_sl_link = get_or_create_na_sl_link(sample_lib,nucacid)

                    bait = get_or_create_bait(row[10])

                    captured_lib = get_or_create_capturedlib(row[9],bait)

                    sl_cl_link = get_or_create_sl_cl_link(sample_lib,captured_lib)

                    sequencing_lib = get_or_create_sequencinglib(row[11])

                    cl_seql_link = get_or_create_cl_seql_link(captured_lib,sequencing_lib)

                    sequencing_run = get_or_create_sequencingrun(**{"name":row[12],"notes":"md5:%s" % row[31]})

                    sequencing_run.sequencing_libs.add(sequencing_lib)

                    create_sequencingfile_for_fastq_files(sample_lib,sequencing_run,row[13],row[14])

                    create_sequencingfile_for_bam_files(sample_lib,sequencing_run,row[32],row[34])

                    create_sequencingfile_for_bai_files(sample_lib,sequencing_run,row[33],row[35])
                except Exception as e:
                    print(str(e))

    else:
        form = AirtableConsolidatedDataForm()
    return render(request, "airtable.html", locals())

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

def create_file_from_file(request):
    file = Path(Path(
        __file__).parent.parent / "uploads" / "report_matching_sample_lib_with_bait_after_reducing_fastq_files.csv")
    df = pd.read_csv(file)
    print(df.columns)
    df['fastq_file'] = df['fastq_file'].str.replace('"', "'").str.replace("'", '"')
    df["fastq_file"] = df["fastq_file"].astype('str')
    df["fastq_file"] = df["fastq_file"].apply(lambda x: make_dict(x))

    df['bam_file'] = df['bam_file'].str.replace('"', "'").str.replace("'", '"')
    df["bam_file"] = df["bam_file"].astype('str')
    df["bam_file"] = df["bam_file"].apply(lambda x: make_dict(x))

    df['bam_bai_file'] = df['bam_bai_file'].str.replace('"', "'").str.replace("'", '"')
    df["bam_bai_file"] = df["bam_bai_file"].astype('str')
    df["bam_bai_file"] = df["bam_bai_file"].apply(lambda x: make_dict(x))

    df[~df["fastq_file"].isnull()].apply(lambda row: get_or_create_files_from_file(row), axis=1)


def leftover(row):

    try:
        SequencingFile.objects.get(name=row["file"])

    except MultipleObjectsReturned:
        # Handle the case where multiple objects were returned
        print("Multiple objects returned. Handle this case appropriately.")

    except ObjectDoesNotExist as e:
        try:
            prefix = row['file'].split("_L0")[0]
            print(prefix, row["file"])
            sequencing_run = row["path"].split("/")[-1] if "HiSeqData_Vivek" in row["path"] else row["path"].split("/")[1]
            set_ = get_or_create_set(
                prefix=prefix,
                path=row['path'],
                sample_lib=SampleLib.objects.get(name="Undefined"),
                sequencing_run=get_or_create_seqrun(name=sequencing_run),
            )
            get_or_create_file(
                sequencing_file_set=set_,
                name=row["file"],
                checksum="",
                type="fastq"
            )
            print("created")
        except Exception as e:
            print(e)


def qpcr_at_leftover(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "df_fq.csv")
    df = pd.read_csv(file)
    df[~df["file"].isnull()].apply(lambda row: leftover(row), axis=1)


def remove_NAN(request):
    from django.db.models import CharField, BooleanField, DateTimeField, DateField, FloatField, TextField
    from django.db.models import Q
    import django.apps
    apps = django.apps.apps.get_models()

    # print(apps)
    for model in apps:
        fields = [f for f in model._meta.fields if isinstance(f, FloatField) or isinstance(f, CharField) or isinstance(f, TextField)]
        # print(fields)
        for field in fields:
            print(model, field.name)
            qs = Q(**{field.name: "NaN"})
            print(model.objects.filter(qs))

def get_barcodes(row):
    try:
        print(row["SL_ID"], row["Old Barcode"], row["New Barcode"])
        if not pd.isnull(row["Old Barcode"]):
            SampleLib.objects.filter(
                    name=row["SL_ID"]).update(barcode=Barcode.objects.get(name=row["Old Barcode"].strip())
                                           )
            return
        if not pd.isnull(row["New Barcode"]):
            SampleLib.objects.filter(
                    name=row["SL_ID"]).update(barcode=Barcode.objects.get(name=row["New Barcode"].strip())
                                           )
            return
    except Exception as e:
        print(e)

def get_baits(row):
    try:
        # print(row["CL_ID"], row["Capture Panel"])
        if "," in row["CL_ID"]:
            for cl in row["CL_ID"].split(","):
                obj = Bait.objects.get(
                    name=row["Capture Panel"].strip()
                )
                CapturedLib.objects.filter(name=cl).update(bait=obj)
            return
        obj = Bait.objects.get(
            name=row["Capture Panel"].strip()
        )
        CapturedLib.objects.filter(name=row["CL_ID"]).update(bait=obj)
    except Exception as e:
        print(e)

def uploads_baits(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "Sample Library with grid view, analysis view and more-Grid view (3).csv")
    df = pd.read_csv(file)
    df[~df["Capture Panel"].isnull()].apply(lambda row: get_baits(row), axis=1)


def get_file_tree(row):

    try:
        if row["HiSeqData/"].strip().endswith(".fastq.gz") | row["HiSeqData/"].strip().endswith(".bam") | row["HiSeqData/"].strip().endswith(".bai"):
            path, file = row["HiSeqData/"].strip().split("-->")
            SequencingFile.objects.get(name=file.strip())
    except ObjectDoesNotExist as e:
        return file
    except:
        return


def upload_file_tree(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "file_tree_with_vivek.txt")
    df = pd.read_csv(file, index_col=False, encoding='iso-8859-1', on_bad_lines = 'warn')
    df["unregistered"] = df.apply(lambda row: get_file_tree(row), axis=1)
    df.to_csv("fastq_files_unregistered.csv", index=False)


def get_new_files(row):
    # prefix = file.split("_L0")[0] if "_L0" in file else file.split("_001")[0] if "_001" in file else None
    if not row["HiSeqData/"].endswith("fastq.gz") or not row["HiSeqData/"].endswith(".bam") or not row["HiSeqData/"].endswith(".bai"):
        return
    try:
        print(row["HiSeqData/"])
        path, file = row["HiSeqData/"].strip().split("-->")
        SequencingFile.objects.get(name=file.strip())
    except:
        print(row["HiSeqData/"])

def match_new_files(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "fastq_files_new.csv")
    df = pd.read_csv(file, index_col=False, encoding='iso-8859-1', on_bad_lines = 'warn')
    # df[~df["new"].isnull()].apply(lambda row: get_new_files(row), axis=1)
    df.apply(lambda row: get_new_files(row), axis=1)


def get_block_scan(row):
    try:
        print(row["Block_ID"])
        dir, scan = row["HE image"].split("=")
        Blocks.objects.filter(name=row["Block_ID"]).update(scan_number=scan)
        print("updated")
    except Exception as e:
        print(e)


def block_scan_number(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "Blocks-Grid view-5.csv")
    df = pd.read_csv(file)
    df[~df["HE image"].isnull()].apply(lambda row: get_block_scan(row), axis=1)


def _files_from_file(row):
    # b=Blocks.objects.filter(block_areas__nucacids__na_sl_links__sample_lib__name=row["sample_lib"])
    try:
        bl = row['Block'].replace("-","_")
        print(bl)
        q = SequencingFile.objects.filter(name__icontains=bl)
        print(set([i.sequencing_file_set.prefix for i in q]))
        # print([i.name for i in b], row["sample_lib"])
        # SampleLib.objects.get(name=row["sample_lib"])

    except:
        print(row["sample_lib"])


def create_fastq_from_file(request):
    file = Path(Path(
        __file__).parent.parent / "uploads" / "report_matching_sample_lib_with_bait_after_reducing_fastq_files.csv")
    df = pd.read_csv(file)
    cols = df.columns
    cols = cols.insert(5, "new_added")
    df['fastq_file'] = df['fastq_file'].str.replace('"', "'").str.replace("'", '"')
    df["fastq_file"] = df["fastq_file"].astype('str')
    df["fastq_file"] = df["fastq_file"].apply(lambda x: make_dict(x))

    df['bam_file'] = df['bam_file'].str.replace('"', "'").str.replace("'", '"')
    df["bam_file"] = df["bam_file"].astype('str')
    df["bam_file"] = df["bam_file"].apply(lambda x: make_dict(x))

    df['bam_bai_file'] = df['bam_bai_file'].str.replace('"', "'").str.replace("'", '"')
    df["bam_bai_file"] = df["bam_bai_file"].astype('str')
    df["bam_bai_file"] = df["bam_bai_file"].apply(lambda x: make_dict(x))

    df.iloc[:48].apply(lambda row: _files_from_file(row), axis=1)
    # df.apply(lambda row: _files_from_file(row), axis=1)
    # df=df[cols]
    # df.to_csv("report_matching_sample_lib_after_IWEI.csv", index=False)
from django.db.models import Q, Count
def get_unregistered(row):
    path,_ = row["HiSeqData/"].split("-->")
    file=row["unregistered"]
    type = "fastq" if file.endswith("fastq.gz") else "bam" if file.endswith(".bam") else "bai"
    if "fastq" in file:
        prefix = file.split("_L0")[0] if "_L0" in file else file.split("_001")[0] if "_001" in file else None
    elif file.endswith(".bai"):
        prefix = file.split(".bai")[0]
    elif file.endswith(".bam"):
        prefix = file.split(".bam")[0]
    prefix = file.split("_L0")[0] if "_L0" in file else prefix

    print(prefix, file)
    try:
        _sr = path.split("/")[1]
        if "Nimblegen" in path:
            _sr = re.sub(r'Nimblegen(\d+) \(BB0*([1-9]\d*)\)', r'Nimblegen\1_BB\2', _sr)
        if "recal" in file:
            match = re.match(r'(\w+)_([ACTG]{6})recal.', file)
            _sl = match.group(1)
            _prefix = f"{match.group(1)}_{match.group(2)}"
            prefix = ((re.sub(r'_\s*\d+ng\s*', ' ', _prefix)).strip()).replace(" _","_")
            _sl = ((re.sub(r'_\s*\d+ng\s*', ' ', _sl)).strip())
        if re.match(r'^H12', file):
            _sl = "H12_22776_B5_Norm"
            print(_sl, prefix)
        if re.match(r'^CGH11', file):
            match = re.match(r'CGH11_(\w+).', file)
            _sl = "CGH11_"+match.group(1)
            print(_sl, prefix)
        if re.match(r'^T12', file):
            match = re.match(r'T12_22597_(\w+)_([ACTG]{6})', file)
            _sl = "T12_22597_"+match.group(1)
            prefix = "T12_22597_"+match.group(1) + "_" + match.group(2)
        sr = SequencingRun.objects.get(name=_sr)
        sl = SampleLib.objects.get(name=_sl)
        set_ = get_or_create_set(
                prefix=prefix,
                path=path,
                sample_lib=sl,
                sequencing_run=sr,
            )
        get_or_create_file(
            sequencing_file_set=set_,
            name=file,
            checksum="",
            type=type
        )
        print("created")
    except MultipleObjectsReturned as e:
        p = ""
        for i in SequencingFileSet.objects.filter(prefix=prefix):
            if i.path == p:
                i.delete()
                print("deleted")
            p=i.path
    except Exception as e:
        print(e)

def upload_unregistered(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "fastq_files_unregistered.csv")
    df = pd.read_csv(file)
    df[~df["unregistered"].isnull()].apply(lambda row: get_unregistered(row), axis=1)

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


def ngs(df2):
    s = df2[df2["HiSeqData/"].str.contains("NGS")]["HiSeqData/"].str.split("-->").str[-1].str.strip()
    f = s.apply(split_and_extract)
    print(type(f))
    print(f.unique())
    return f.unique()

def ngs2(df2, row):
    if not row['sample_lib'].startswith('NGS'):
        return row
    s = df2[df2["HiSeqData/"].str.contains(row["sample_lib"])]["HiSeqData/"].str.split("-->", expand=True)
    if row["sample_lib"] == "NGS-2-1" or row["sample_lib"] == "NGS_1_1":
        s = df2[df2["HiSeqData/"].str.contains(row["sample_lib"]+"_")]["HiSeqData/"].str.split("-->", expand=True)

    seqr = s[0].tolist()[0].split("/")[1]
    row["captured_lib"] = seqr.split("_")[1]
    row["Bait"] = "NimV2mix3"
    row["sequencing_lib"] = seqr.split("_")[1]
    row["sequencing_run"] = seqr
    row["fastq_file"] = {i: "" for i in s[1].tolist()}
    row["fastq_path"] = s[0].tolist()[0]
    row["area_type"] = "tumor"
    return row


def prepare_report(request):
    file = Path(Path(
        __file__).parent.parent / "uploads" / "report_matching_sample_lib_with_bait_after_reducing_fastq_files.csv")
    df = pd.read_csv(file)
    df = df.drop(['Input Conc.'], axis=1)

    file2 = Path(Path(__file__).parent.parent / "uploads" / "file_tree_with_vivek.txt")
    df2 = pd.read_csv(file2, index_col=False, encoding='iso-8859-1', on_bad_lines='warn')
    df2 = df2[df2['HiSeqData/'].str.strip().str.endswith('.fastq.gz')]

    df3 = pd.DataFrame(columns=list(df.columns))
    df3["sample_lib"] = ngs(df2)
    df = pd.concat([df, df3], ignore_index=True)
    # print(df)
    #
    # df.loc[:48, 'sample_lib'] = df.loc[:48].apply(lambda row: refactor_samplelib(row), axis=1)
    # df.to_csv(file, index=False)

    df['fastq_file'] = df['fastq_file'].str.replace('"', "'").str.replace("'", '"')
    df["fastq_file"] = df["fastq_file"].astype('str')
    df["fastq_file"] = df["fastq_file"].apply(lambda x: make_dict(x))

    df['bam_file'] = df['bam_file'].str.replace('"', "'").str.replace("'", '"')
    df["bam_file"] = df["bam_file"].astype('str')
    df["bam_file"] = df["bam_file"].apply(lambda x: make_dict(x))

    df['bam_bai_file'] = df['bam_bai_file'].str.replace('"', "'").str.replace("'", '"')
    df["bam_bai_file"] = df["bam_bai_file"].astype('str')
    df["bam_bai_file"] = df["bam_bai_file"].apply(lambda x: make_dict(x))
    print(df[df['sample_lib'].str.startswith('CP-')].index)
    print(df[df['sample_lib'].str.startswith('NGS')].index)

    df = df.apply(lambda row: ngs2(df2, row), axis=1)
    # df = df.apply(lambda row: get_fastq_t12(row), axis=1)
    # df = df.apply(lambda row: get_bam_empty(row), axis=1)
    # df = df.apply(lambda row: get_bai_empty(row), axis=1)

    # df.to_csv("df.csv", index=False)
    # df[~df["fastq_file"].isnull()].apply(lambda row: get_fastq_empty(row), axis=1)
    # df.columns = df[cols]
    df_1 = df.iloc[:1331]
    df_2 = df.iloc[1343:]
    df_3 = df.iloc[4343:]
    df = pd.concat([df_1, df_3, df_2]).reset_index(drop=True)
    df.to_csv("df.csv", index=False)


def get_sex(value):
    return value.lower() if value and len(value) == 1 else None


def get_race(value):
    for x in Patients.RACE_TYPES:
        if value.lower() == x[1].lower():
            return x[0]
    return 7

def get_or_create_patient(**kwargs):
    try:
        return Patients.objects.get(pat_id=kwargs["pat_id"])
    except ObjectDoesNotExist as e:
        return Patients.objects.create(**kwargs)


def get_area_type(value):
    for x in Areas.AREA_TYPE_TYPES:
        if value.lower() == x[1].lower():
            return x[0]
    return None


def we(row):
    match = re.search(r'-BND\s+(\d+)\.00', row["NA_ID"])

    def replace_with_formatted_number(match):
        numeric_value = int(match.group(1))
        formatted_value = f"{numeric_value:03}"
        return f'BND-{formatted_value}'

    if match:
        # print(row["sample_lib"])
        value = re.sub(r'-BND\s+(\d+)\.00', replace_with_formatted_number, row["NA_ID"])
        print(f"value: {value}")
        return value


def nas(row):
    try:
        if "BND" in row["NA_ID"]:
            na=NucAcids.objects.get(name=we(row))
        else:
            na = NucAcids.objects.get(name=row["NA_ID"])
        if "," in row["Area ID"]:
            if "2409 SCC, in situ" in row["Area ID"]:
                a = Areas.objects.get(name="2409 SCC, in situ")
                AREA_NA_LINK.objects.get_or_create(nucacid=na, area=a)
                return
            if "426 blue nevus, cellular,  DF like" in row["Area ID"]:
                a = Areas.objects.get(name="426 blue nevus, cellular,  DF like")
                AREA_NA_LINK.objects.get_or_create(nucacid=na, area=a)
                return
            if "436 common, sclerotic dermal component" in row["Area ID"]:
                a = Areas.objects.get(name="436 common, sclerotic dermal component")
                AREA_NA_LINK.objects.get_or_create(nucacid=na, area=a)
                return
            for area in row["Area ID"].split(","):
                print(na, area)
                a = Areas.objects.get(name=area.strip())
                AREA_NA_LINK.objects.get_or_create(nucacid=na, area=a)
    except Exception as e:
        print(e,row["NA_ID"], row["Area ID"])


def check_na(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "Nucleic Acids-Grid view (1).csv")
    df = pd.read_csv(file)
    for na in NucAcids.objects.filter(Q(area_na_links__area__name="UndefinedArea")):
        if na.area_na_links.count() > 1:
            oldest_child = na.area_na_links.filter(area__name="UndefinedArea").first()
            oldest_child.delete()
    df[~df["NA_ID"].isnull() & ~df["Area ID"].isnull()].apply(lambda row: nas(row), axis=1)


def nas2(row):
    try:
        sl = SampleLib.objects.get(name=row["Sample"])
        na, _ = NucAcids.objects.get_or_create(name=row['NA_id'])
        b = Blocks.objects.get(name=row["Block"])
        # print(b.patient)
        if not pd.isnull(row["pat_id"]):
            patient = Patients.objects.get(pat_id=str(row["pat_id"]).replace(".0", ""))
            # print(patient)
            b.patient = patient
        _notes = f"SITE_CODE: {row['site_code']} / icd9: {row['icd9']} / DEPT_NUMBER: {row['dept_number']} / SPECIMEN: {row['specimen']} / DX_TEXT: {row['dx_text']}"
        b.age = row["pat_age"] if not pd.isnull(row["pat_age"]) else b.age
        b.notes = str(row["Notes/Other"]) + str(row["note"]) + str(_notes)
        b.micro = row["micro"] if not pd.isnull(row["micro"]) else b.micro
        b.diagnosis = row["Diagnosis"] if not pd.isnull(row["Diagnosis"]) else b.diagnosis
        b.thickness = row["thickness"] if not pd.isnull(row["thickness"]) else b.thickness
        b.mitoses = row["mitoses"] if not pd.isnull(row["mitoses"]) else b.mitoses
        b.p_stage = row["p_stage"] if not pd.isnull(row["p_stage"]) else b.p_stage
        b.prim = row["prim"] if not pd.isnull(row["prim"]) else b.prim
        b.subtype = row["subtype"] if not pd.isnull(row["subtype"]) else b.subtype
        b.save()
        area, _ = Areas.objects.get_or_create(name=row["Area_id"], block=b)
        area.block = b
        area.area_type = get_area_type(row['Area'])
        area.save()
        link_area, _ =AREA_NA_LINK.objects.get_or_create(area=area,nucacid=na)
        link_sl_na, _ = NA_SL_LINK.objects.get_or_create(sample_lib=sl,nucacid=na)
    except Exception as e:
        print(e,row["Sample"])


def check_na2(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "Consolidated_data_final.csv")
    df = pd.read_csv(file)
    df[~df["NA_id"].isnull()].apply(lambda row: nas2(row), axis=1)


def nas3(row):

    try:
        if not pd.isnull(row['NA_ID_x']):
            if "," in row['NA_ID_x'].replace(";",","):
                for na in row['NA_ID_x'].replace(";", ",").split(","):
                    NucAcids.objects.get(name=na)
        if not pd.isnull(row['NA_ID_y']):
            if "," in row['NA_ID_y'].replace(";",","):
                for na in row['NA_ID_y'].replace(";", ",").split(","):
                    NucAcids.objects.get(name=na)
        if not pd.isnull(row['NA_id']):
            if "," in row['NA_id'].replace(";",","):
                for na in row['NA_id'].replace(";", ",").split(","):
                    NucAcids.objects.get(name=na)
        if not pd.isnull(row['Area_id']):
            area=Areas.objects.get(name=row["Area_id"])
        if not pd.isnull(row['Area_ID']):
            area=Areas.objects.get(name=row["Area_ID"])
        # link=AREA_NA_LINK.objects.get_or_create(area=area,nucacid=na)
    except Exception as e:
        print(e)
        print(row['NA_ID_x'], row['NA_ID_y'], row['NA_id'])


def check_na3(request):
    for na in NucAcids.objects.filter(name__endswith="_NA"):
        # print(na)
        name = "NA_"+na.name.replace("_NA","")
        # print(name)
        c = NucAcids.objects.filter(name=name).count()
        if c==1:
            print([na.name for na in NucAcids.objects.filter(name__icontains=na.name.replace("_NA",""))])
    # for na in NucAcids.objects.filter(area_na_links__area__name="UndefinedArea"):
    #     b = Blocks.objects.filter(name__icontains=na.name.replace("_NA",""))
    #     if len(b)==1:
    #         print(na.name, b.first().block_areas.all(),sep="------")
    #         if len(b.first().block_areas.all())==1:
    #             AREA_NA_LINK.objects.filter(area__name="UndefinedArea", nucacid=na).delete()
    #             AREA_NA_LINK.objects.get_or_create(area=b.first().block_areas.first(), nucacid=na)
    # print(NucAcids.objects.filter(area_na_links__area__name="UndefinedArea").count())
    file = Path(Path(__file__).parent.parent / "uploads" / "patients_done.csv")
    df = pd.read_csv(file)
    # df[~df["NA_ID_x"].isnull()].apply(lambda row: nas3(row), axis=1)
    # df[~df["NA_id"].isnull() & ~df["Area_id"].isnull()].apply(lambda row: nas2(row), axis=1)


def patients(row):
    try:

        blocks = Blocks.objects.filter(patient__isnull=True)
        for block in blocks:
            patient_id = "_G"
            patient, created = Patients.objects.get_or_create(pat_id=patient_id)
            block.patient = patient
            block.save()
            print("created")
    except Exception as e:
        print(row["block"],e)


def check_patient(request):
    for na in NucAcids.objects.all():
        print(na)
        obj, created = AREA_NA_LINK.objects.get_or_create(nucacid=na,area=na.area)
    # file = Path(Path(__file__).parent.parent / "uploads" / "report_patients_not_matched.csv")
    # df = pd.read_csv(file)
    # df.apply(lambda row: patients(row), axis=1)



def check_blocks(row):
    try:
        print(row["name"])
        b = Blocks.objects.get(name=row["name"])
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
    for x in Blocks.COLLECTION_CHOICES:
        if value.lower() == x[1].lower():
            return x[0]
    return Blocks.SCRAPE


def check_blocks2(row):
    try:
        mapping_ulcreation={
            'negative':False,
            'Present':True,
        }
        print(row["Block_ID"])
        s= "HE image	Specimen site	"
        b = Blocks.objects.get(name=row["Block_ID"])
        notes=b.notes
        _notes=f"Description: {row['Description']} / Block storage location: {row['Block storage location']} / Specimen site: {row['Specimen site']}"
        b.notes=str(row["Notes"]) + str(_notes) + str(notes)
        b.diagnosis=row["Diagnosis/Type"] if not pd.isnull(row["Diagnosis/Type"]) else b.diagnosis
        b.collection=get_collection(row["Collection Method"]) if not pd.isnull(row["Collection Method"]) else b.collection
        b.fixation=row["Fixation"] if not pd.isnull(row["Fixation"]) else b.fixation
        b.slides=row["Slides"] if not pd.isnull(row["Slides"]) else b.slides
        b.slides_left=row["Slides left"] if not pd.isnull(row["Slides left"]) else b.slides_left
        b.ulceration=mapping_ulcreation[row["Ulceration"]] if not pd.isnull(row["Ulceration"]) else b.ulceration
        b.save()
    except Exception as e:
        print(row["Block_ID"],e)


def check_block2(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "Blocks-Grid view-5.csv")
    df = pd.read_csv(file)
    df.apply(lambda row: check_blocks2(row), axis=1)


def check_blocks3(row):
    try:
        mapping_ulcreation={
            'negative':False,
            'Present':True,
        }
        print(row["Block"])
        b = Blocks.objects.get(name=row["Block"])
        notes=b.notes
        _notes=f"SITE_CODE: {row['site_code']} / icd9: {row['icd9']} / DEPT_NUMBER: {row['dept_number']} / SPECIMEN: {row['specimen']} / DX_TEXT: {row['dx_text']}"
        b.age = row["pat_age"] if not pd.isnull(row["pat_age"]) else b.age
        b.notes=str(row["Notes/Other"]) + str(row["note"]) + str(_notes) + str(notes)
        b.micro = row["micro"] if not pd.isnull(row["micro"]) else b.micro
        b.diagnosis=row["Diagnosis"] if not pd.isnull(row["Diagnosis"]) else b.diagnosis
        b.thickness = row["thickness"] if not pd.isnull(row["thickness"]) else b.thickness
        b.mitoses = row["mitoses"] if not pd.isnull(row["mitoses"]) else b.mitoses
        b.p_stage = row["p_stage"] if not pd.isnull(row["p_stage"]) else b.p_stage
        b.prim = row["prim"] if not pd.isnull(row["prim"]) else b.prim
        b.subtype = row["subtype"] if not pd.isnull(row["subtype"]) else b.subtype
        b.save()
    except Exception as e:
        print(row["Block"],e)


def check_block3(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "Consolidated_data_final.csv")
    df = pd.read_csv(file)
    df[~df["Block"].isnull()].apply(lambda row: check_blocks3(row), axis=1)


def get_all_md5(row):
    # print(row)
    try:
        if "==" in row["md5"]:
            _file, md5 = row["md5"].split("==")
            file = _file.replace(".md5", "")
        elif "coldstorage" in row["md5"]:
            md5, _file = (','.join(row["md5"].split())).split(",")
            file = _file.split("/")[-1]
        else:
            md5, _file = (','.join(row["md5"].split())).split(",")
            file = _file.replace("./", "").replace("*", "").replace("R_SGLP", "SGLP")
        checksum = SequencingFile.objects.get(name=file).checksum
        if checksum == None or checksum == "":
            f = SequencingFile.objects.get(name=file)
            f.checksum = md5
            f.save()
            print("saved")
    except Exception as e:
        print("===", e, row["md5"])

def upload_file_tree_all_md5(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "all_md5.txt")
    df = pd.read_csv(file, index_col=False, encoding='iso-8859-1', on_bad_lines = 'warn')
    # print(df)
    df[~df["md5"].isnull()].apply(lambda row: get_all_md5(row), axis=1)


def get_sample_library(row):
    try:
        if pd.isnull(row["Sample"]) or pd.isnull(row["Area_id"]) or pd.isnull(row["NA_id"]):
            return
        sl=SampleLib.objects.get(name=row["Sample"])
        area,_ = Areas.objects.get_or_create(name=row['Area_id'])
        na,_ = NucAcids.objects.get_or_create(name=row['NA_id'])
        AREA_NA_LINK.objects.get_or_create(area=area, nucacid=na)
        NA_SL_LINK.objects.get_or_create(sample_lib=sl, nucacid=na)
    except ObjectDoesNotExist as e:
        print(e, row['Sample'], row['NA_id'])
    except MultipleObjectsReturned as e:
        pass

def check_sl_bait(row):
    if row['sequencing_run']=='BCB036':
        row["Bait"] = 'Small Gene Panel'

def check_sample_library(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "report_matching_sample_lib_with_bait_after_reducing_fastq_files.csv")
    df = pd.read_csv(file)
    df.apply(lambda row: check_sl_bait(row), axis=1)
    # from .Acral_melanoma_lines_mRNA_Seq_AL1806051_R1 import create_file
    # create_file()
    df.to_csv("uploads/report_matching_sample_lib_with_bait_after_reducing_fastq_files2.csv", index=False)


def check_seq_run_2(row):
    # print(row)
    try:
        SequencingRun.objects.get(name=row["seq_runs"])
    except Exception as e:
        print(row["seq_runs"], e)


def check_seq_run(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "seq_runs.txt")
    df = pd.read_csv(file)
    for i in SequencingRun.objects.all():
        name = i.name
        i.name = name.strip()
        i.save()
    # df = pd.read_csv(file, index_col=False, encoding='iso-8859-1', on_bad_lines='warn')
    df.apply(lambda row: check_seq_run_2(row), axis=1)
    print(df.count())
    # from .Acral_melanoma_lines_mRNA_Seq_AL1806051_R1 import create_file
    # create_file()
    # df.to_csv("uploads/report_matching_sample_lib_with_bait_after_reducing_fastq_files2.csv", index=False)


def get_check_dna_rna(row):
    try:
        sl = SampleLib.objects.get(name=row["sample_lib"])
        na = NA_SL_LINK.objects.filter(sample_lib=sl, nucacid__na_type__isnull=False)
        # print(row["sample_lib"], na.name, na.na_type)
        if na:
            row["RNA/DNA"] = na[0].nucacid.na_type.upper()
        else:
            row["RNA/DNA"] = ""
        return row
    except Exception as e:
        print(e, row["sample_lib"])


def check_dna_rna(request):
    file = Path(Path(__file__).parent.parent / "uploads" / "SequencingSampleSheet-01102024.xlsx")
    file = "/Users/cbagci/Library/Containers/com.apple.mail/Data/Library/Mail Downloads/0B0A3920-A69F-4FFD-9560-AB728F303574/SequencingSampleSheet-01102024.xlsx"
    file = Path(Path(__file__).parent.parent / "uploads" / "RNA_libraries.csv")
    df = pd.read_csv(file)
    print(df)
    df = df.apply(lambda row: get_check_dna_rna(row), axis=1)
    df.to_csv("SequencingSampleSheet-01102024_v3.csv")

    # df = pd.read_excel(file,sheet_name=0)
    # df = df.dropna(subset=['sample_lib'])
    # df = df.dropna(subset=['sample_lib'])





