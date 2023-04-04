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
from libprep.models import NucAcids
from method.models import Method
from samplelib.models import SampleLib, NA_SL_LINK
from capturedlib.models import CapturedLib, SL_CL_LINK
from bait.models import Bait
from barcodeset.models import Barcodeset,Barcode
from sequencingrun.models import SequencingRun
from sequencinglib.models import SequencingLib,CL_SEQL_LINK
from django.core.exceptions import ObjectDoesNotExist
import json

def migrate(request):

    if request.method=="POST":
        form = MigrationForm(request.POST, request.FILES)

        if form.is_valid():

            app = form.cleaned_data["app"]

            file = form.cleaned_data["file"].read().decode('utf-8')

            report = []
            reader = csv.reader(StringIO(file))
            next(reader) #skip first row

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
                                    qs = Projects.objects.filter(abbreviation__startswith=l[1])
                                    if qs.exists():
                                        return "%s-%d" % (l[1],len(qs))
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
                            sex=get_sex(row[1]),
                            race=get_race(row[3]),
                            source=row[4],
                            notes=row[7]
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

                        def get_ulceration(value):
                            return True if value else False

                        def get_notes(notes,description):
                            return "%s, Alternative Block IDs:%s" % (notes,description) if description else notes

                        def get_slides(value):
                            return int(value) if value else None

                        def get_slides_left(value):
                            return int(value) if value else None

                        Blocks.objects.create(
                            name=row[0].strip(),
                            patient=get_patient(row[1].strip()),
                            project=get_project(row[10].strip()),
                            old_body_site=row[3].strip(),
                            ulceration=get_ulceration(row[4].strip()),
                            slides=get_slides(row[5]),
                            slides_left=get_slides_left(row[6]),
                            fixation=row[7],
                            storage=row[13],
                            scan_number=row[2],
                            diagnosis=row[11],
                            notes=get_notes(row[14],row[12]),
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

                        NucAcids.objects.create(
                            name=row[0].strip(),
                            area=get_area(row[1].strip()),
                            date=get_date(row[3].strip()),
                            method=get_or_create_method(row[4].strip()),
                            na_type=get_na_type(row[2].strip()),
                            conc=row[5],
                            vol_init=row[6],
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

                        sl = SampleLib.objects.create(
                            name=row[0].strip(),
                            barcode=get_barcode(row[22].strip()),
                            date=get_date(row[23]),
                            qpcr_conc=row[8],
                            amount_final=row[13],
                            vol_init=row[9],
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
                    elif app == "barcode":
                        Barcode.objects.create(
                            barcode_set=Barcodeset.objects.get(name="New Barcodes"),
                            name=row[0],
                            i5=row[3],
                            i7=row[2]
                        )

                    print("migrated..")
                    report.append({"name":row[0],"status":"OK","message":""})
                except Exception as e:
                    print(str(e))
                    print(row)
                    report.append({"name":row[0],"status":"FAILED","message":str(e)})

            print("Process was completed successfully")

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
            print("Process wasn't completed!")
    else:
        form = MigrationForm()

    return render(request,"migration.html",locals())

def report(request):
    import csv
    from io import StringIO

    report = []
    i = 1

    for seq_r in SequencingRun.objects.all():
        for seq_l in seq_r.sequencing_libs.all():
            for cl_seql_link in seq_l.cl_seql_links.all():
                for sl_cl_link in cl_seql_link.captured_lib.sl_cl_links.all():
                    sample_lib = sl_cl_link.sample_lib
                    captured_lib = sl_cl_link.captured_lib
                    print(i)
                    i += 1
                    for na_sl_link in sample_lib.na_sl_links.filter(nucacid__na_type=NucAcids.DNA):
                        nucacid = na_sl_link.nucacid
                        report.append({
                            "sample_lib": sample_lib.name,
                            "barcode": sample_lib.barcode.name,
                            "i5": sample_lib.barcode.i5,
                            "i7": sample_lib.barcode.i7,
                            "sequencing_run": seq_r.name,
                            "na_type": nucacid.get_na_type_display() if nucacid.na_type else None,
                            "area_type": nucacid.area.get_area_type_display() if nucacid.area and nucacid.area.area_type else None,
                            "patient": nucacid.area.block.patient.pat_id if nucacid.area and nucacid.area.block and nucacid.area.block.patient else None,
                            "bait": captured_lib.bait.name if captured_lib.bait else None
                        })


    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="report-sl-review.csv"'},
    )

    field_names = ["sample_lib","barcode","i5","i7","sequencing_run","na_type","area_type","patient","bait"]
    writer = csv.writer(response)
    writer.writerow(field_names)
    for item in report:
        writer.writerow([item[field] for field in field_names])

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
