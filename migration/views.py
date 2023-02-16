from django.shortcuts import render, redirect
from .forms import *

def migrate(request):
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
    from barcodeset.models import Barcode
    from sequencingrun.models import SequencingRun

    if request.method=="POST":
        form = MigrationForm(request.POST, request.FILES)

        if form.is_valid():

            app = form.cleaned_data["app"]

            file = form.cleaned_data["file"].read().decode('utf-8')

            reader = csv.reader(StringIO(file))
            report = []

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
                            name=row[1],
                            abbreviation=get_abbreviation(row[1]),
                            pi=get_pi(row[2]),
                            speedtype="",
                            description=row[0],
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

                        if row[0] != "":
                            patient = Patients.objects.create(
                                pat_id=row[0],
                                sex=get_sex(row[1]),
                                race=get_race(row[3]),
                                source=row[4],
                                notes=row[7]
                            )

                            report.append({"name":row[0],"status":"OK"})
                        else:
                            report.append({"name":row[0],"status":"PASS"})
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
                            name=row[0],
                            patient=get_patient(row[1]),
                            project=get_project(row[10]),
                            old_body_site=row[3],
                            ulceration=get_ulceration(row[4]),
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

                        print("block:",get_block(row[2]))
                        print("type:",get_area_type(row[4]))
                        print("date:",get_completion_date(row[7]))

                        Areas.objects.create(
                            name=row[0],
                            block=get_block(row[2]),
                            area_type=get_area_type(row[4]),
                            completion_date=get_completion_date(row[7]),
                            notes=row[9],
                        )

                        Blocks.objects.filter(name=row[2]).update(collection=get_collection(row[3]))
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
                            name=row[0],
                            area=get_area(row[1]),
                            date=get_date(row[3]),
                            method=get_or_create_method(row[4]),
                            na_type=get_na_type(row[2]),
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
                            name=row[0],
                            barcode=get_barcode(row[22]),
                            date=get_date(row[23]),
                            qpcr_conc=row[8],
                            amount_final=row[13],
                            vol_init=row[9],
                            notes=row[24],
                        )

                        create_na_sl_link(sl,row[1],row[10],row[8])

                        cl = create_cl(row[14],row[20],row[14],row[19])

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

                        SequencingRun.objects.create(
                            name = row[1],
                            date = get_date(row[2]),
                            facility = row[3],
                            sequencer = get_sequencer(row[4]),
                            pe = get_pe(row[4]),
                            notes = row[9]
                        )

                    print("migrated..")
                except Exception as e:
                    print(str(e))
                    print(row)
                    report.append({"name":row[0],"status":"FAILED"})
                    pass

            print("Process was completed successfully")

        else:
            print("Process wasn't completed!")
    else:
        form = MigrationForm()

    return render(request,"migration.html",locals())
