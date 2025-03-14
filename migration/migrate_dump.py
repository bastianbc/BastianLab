import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test1.settings')
django.setup()
from lab.models import Patient
from projects.models import Project
from areas.models import Area
from libprep.models import NucAcids, AREA_NA_LINK
from samplelib.models import SampleLib, NA_SL_LINK
from capturedlib.models import CapturedLib, SL_CL_LINK
from barcodeset.models import Barcodeset,Barcode
from sequencinglib.models import SequencingLib,CL_SEQL_LINK
from sequencingfile.models import SequencingFile, SequencingFileSet
from body.models import *
import string
import random
import re
import psycopg2
from psycopg2 import OperationalError
from pathlib import Path
import pandas as pd


class MigrateDump():
    database_name = "migration3_dump"
    database_user = "testuser"
    database_password = '1235'
    database_host = "localhost"
    database_port = "5432"

    @staticmethod
    def get_or_none(model_class, **kwargs):
        try:
            return model_class.objects.get(**kwargs)
        except Exception as e:
            return None

    @classmethod
    def connection(cls):
        """Create a database connection to a PostgreSQL database"""
        connection = None
        try:
            connection = psycopg2.connect(
                database=cls.database_name,
                user=cls.database_user,
                password=cls.database_password,
                host=cls.database_host,
                port=cls.database_port,
            )
            print("Connection to PostgreSQL DB successful")
        except OperationalError as e:
            print(f"The error '{e}' occurred")
        return connection

    @classmethod
    def connection_ucsf(cls):
        connection= None
        try:
            connection = psycopg2.connect(
                database = "labdb",
                user="testuser",
                password="1235",
                host='10.65.11.68',
                port='5432',
            )
            print("Connection to UCSF PostgreSQL DB successful")
        except OperationalError as e:
            print(f"The error '{e}' occurred")
        return connection


    @classmethod
    def cursor(cls, sql_statement):
        conn = cls.connection()
        cur = conn.cursor()
        cur.execute(sql_statement)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    @staticmethod
    def get_race(value):
        for x in Patient.RACE_TYPES:
            if value.lower() == x[1].lower():
                return x[0]
        return 7

    @staticmethod
    def register_patients():

        rows = MigrateDump().cursor("SELECT * FROM patients")
        for row in rows:
            try:
                # print(row)
                # print(row[0])
                # patient = Patient.objects.get(pat_id=row[0])
                patient, created = Patient.objects.get_or_create(
                    pat_id=row[0]
                )

                if row[1] is not None:
                    # print(row[1])
                    sex = "" if row[1] is None else row[1].lower() if row[1] else ""
                    # print(sex)
                    patient.sex = sex if sex in ["m", "f"] else ""
                if row[3] is not None:
                    patient.race = MigrateDump().get_race(row[3])
                patient.source = row[4] or ""
                patient.notes = row[6] or ""
                # patient.id = row[7]
                patient.pat_ip_id = row[9] or ""
                patient.save()
                # print(patient, "saved")
            except Exception as e:
                print(row[0], e)

    @staticmethod
    def get_collection(value):
        for x in Block.COLLECTION_CHOICES:
            if value.lower() == x[1].lower():
                return x[0]
        return Block.SCRAPE

    @staticmethod
    def get_abbreviation(name):
        lookup = [
            [["Acral melanoma"], "AM"],
            [["Acral melanoma cell lines"], "AMCL"],
            [["Nevus library", "Café aul lait", "lentiginous nevi"], "NL"],
            [["Melanoma outcome study", "California Registry", "Melanoma prognosis"], "MOS"],
            [["Conjunctival Melanoma"], "CONJ"],
            [["Dysplastic nevus"], "DN"],
            [["Progression", "Melanoma evolution", "Melanoma epigenetics"], "PROG"],
            [["Dirk Hi-C"], "DHC"],
            [["Nodular melanoma"], "NM"],
            [["Oral melanoma"], "OM"],
            [["Spitz melanoma"], "SM"],
            [["Sclerotic nevi"], "SCL"],
            [["Werner Syndrome"], "WS"],
            [["Seattle"], ""],
            [["KIT"], "KIT"],
            [["Iwei Medley", "Fusion RNA", "Possible TERT fusion", "Seattle", "Atypical Spitz Progression",
              "PRKC fused cases", "NRAS amplified", "Deep Penetrating Melanoma", "Clinical cases BCC",
              "spatial gene expression", "Fusion RNA"], "FUS"],
            [["CGH Validation"], "CGH"],
            [["Melanocytic Nevus"], "MNE"],
            [["Chromium Single Cell Gene Expression Flex"], "CSCGEF"],
        ]
        for l in lookup:
            if name.lower().strip() in [x.lower() for x in l[0]]:
                # qs = Project.objects.filter(abbreviation__startswith=l[1])
                # if qs.exists():
                #     return "%s-%d" % (l[1],len(qs))
                return l[1]

        return ''.join(random.choices(string.digits, k=5))

    @staticmethod
    def register_blocks():
        rows = MigrateDump().cursor("SELECT * FROM blocks")
        # print(Patient.objects.all().count())
        count = 0
        for row in rows:
            count += 1
            try:
                # print(row[-4])
                patient = Patient.objects.get(pat_id=row[-4])
                block, created = Block.objects.get_or_create(
                    name=row[1].strip()
                )
                block.patient = patient
                block.age = row[2]
                # block.body_site =
                block.ulceration = row[3]
                block.thickness = row[4]
                block.mitoses = row[5]
                block.p_stage = row[6] if row[6] is not None else None
                if row[7] != None:
                    block.prim = row[7].lower() if row[7].lower() in [item[0].lower() for item in Block.PRIM_TYPES] else None
                block.subtype = row[8]
                block.slides = row[9]
                block.slides_left = row[10]
                block.fixation = row[11]
                block.storage = row[12]
                if row[13] != None:
                    if "=" in row[13]:
                        block.scan_number = row[13].split("=")[-1]
                    else:
                        block.scan_number = row[13].split("/")[-1]
                    if block.scan_number.startswith(","):
                        block.scan_number = block.scan_number[1:]
                block.icd10 = row[14]
                block.diagnosis = row[15]
                block.notes = row[16]
                block.micro = row[17]
                block.gross = row[18]
                block.clinical = row[19]
                block.old_body_site = row[21]
                # if row[22] != None:
                #     block.collection = MigrateDump.get_collection(row[22])
                block.path_note = row[23]
                block.ip_dx = row[24]
                if row[-3] != None:
                    project = Project.objects.filter(name=row[-3]).first()
                    if not project:
                        project = Project.objects.create(name=row[-3], abbreviation=MigrateDump.get_abbreviation(row[-3]))
                    block.project = project
                block.save()
                print(count, block)
            except Exception as e:
                print(e, row[-3])

    @staticmethod
    def get_area_type(value):
        for x in Area.AREA_TYPE_TYPES:
            if value.lower() == x[1].lower():
                return x[0]
            else:
                return value[:29].lower()

        return None

    @staticmethod
    def register_areas():
        sql = '''
        SELECT a.*, l.*, b.name as block, b.bl_id
        FROM AREAS a
        LEFT JOIN block_area_link l on a.id=l.area
        LEFT JOIN blocks b on l.block = b.bl_id
        '''
        rows = MigrateDump().cursor(sql)

        sql2 = '''SELECT * FROM AREAS'''
        rows2 = MigrateDump().cursor(sql2)

        for row in rows:
            try:
                if row[0] != None:
                    area, _ = Area.objects.get_or_create(name=row[1])
                    # area.block = block
                    # area.save()
                    if row[2] != None:
                        area.area_type = MigrateDump.get_area_type(row[2])
                    area.image = row[4]
                    area.notes = row[5]
                    area.save()
                # print(row)
            except Exception as e:
                print(e,row[1], "Block: ",row[-2])
                try:
                    if row[-6] is not None:
                        for i in row[-6].split(","):
                            block, _ = Block.objects.get_or_create(name=i)
                    area, _ = Area.objects.get_or_create(name=row[1])
                    # area.block = block
                    # area.save()
                    if row[2] != None:
                        area.area_type = MigrateDump.get_area_type(row[2])
                    area.image = row[4]
                    area.notes = str(row[5]) + " additional blocks: " + str(row[6])
                    area.save()
                    print(block,"^^^^")
                except Exception as e:
                    print(e)
        # for row in rows2:
        #     try:
        #         area = Areas.objects.get(name=row[1])
        #         if row[2] != None:
        #             area.area_type = MigrateDump.get_area_type(row[2])
        #         area.image = row[4]
        #         area.notes = row[5]
        #         area.save()
        #         if not area:
        #             print(row[1], " - ", row[-1])
        #             block = Block.objects.get(name=row[-1].strip())
        #             # if "," in row[-1]:
        #             #     for i in row[-1].split(","):
        #             #         print(i)
        #             #         block = Block.objects.get(name=i)
        #             area, _ = Areas.objects.get_or_create(name=row[1],block=block)
        #             if row[2] != None:
        #                 area.area_type = MigrateDump.get_area_type(row[2])
        #             area.image = row[4]
        #             area.notes = row[5]
        #             if row[2] != None:
        #                 area.area_type = MigrateDump.get_area_type(row[2])
        #             area.image = row[4]
        #             area.notes = row[5]
        #             area.save()
        #         else:
        #             print(row)
        #             print(row[-1])
        #             if "," in row[-1]:
        #                 for i in row[-1].split(","):
        #                     # print("%%%",i)
        #                     block = Block.objects.get(name=i)
        #                     area = Areas.objects.get(name=row[1])
        #                     area.block=block
        #                     if row[2] != None:
        #                         area.area_type = MigrateDump.get_area_type(row[2])
        #                     area.image = row[4]
        #                     area.notes = row[5]
        #                     area.save()
        #             else:
        #                 # print("iii")
        #                 block = MigrateDump.get_or_none(Block, name=row[-1])
        #                 if not block:
        #                     block = MigrateDump.get_or_none(Block, name="BB"+row[-1])
        #                 if block:
        #                     area = Areas.objects.get(name=row[1])
        #                     area.block = block
        #                     if row[2] != None:
        #                         area.area_type = MigrateDump.get_area_type(row[2])
        #                     area.image = row[4]
        #                     area.notes = row[5]
        #                     area.save()
            # except Exception as e:
            #     print("{} area:{}, block{}".format(e, row[1], row[-1]))

    @staticmethod
    def get_na_type(value):
        for x in NucAcids.NA_TYPES:
            if value.lower() == x[1].lower():
                return x[0]
        return None

    @staticmethod
    def register_nuc_acids():
        sql = '''
            SELECT n.*, nl.*, a.name FROM AREAS a
            LEFT JOIN area_na_link nl on nl.area_id = a.id
            LEFT JOIN nuc_acids n on n.id = nl.nucacid_id
            WHERE nucacid_id is not NULL
            order by n.name
        '''
        sql2 = '''
            SELECT * FROM nuc_acids
        '''
        sql3 = '''
            SELECT nl.* ,
            a.name as area,
            n.name as nuc_acid FROM area_na_link nl
            LEFT JOIN nuc_acids n on n.id = nl.nucacid_id
            LEFT JOIN areas a on a.id = nl.area_id
            WHERE nucacid_id is not NULL AND
            area_id is not NULL
        '''
        rows = MigrateDump().cursor(sql)
        rows2 = MigrateDump().cursor(sql2)
        rows3 = MigrateDump().cursor(sql3)
        for row in rows:
            # try:
                # print(row)
                if row[-1] != None:
                    area = Areas.objects.get(name=row[-1])
                if row[3] != None:
                    na_type = MigrateDump.get_na_type(row[3])
                    nuc_acid, _ = NucAcids.objects.get_or_create(name=row[1],na_type=na_type)
                else:
                    nuc_acid, _ = NucAcids.objects.get_or_create(name=row[1])
                link = AREA_NA_LINK.objects.get_or_create(
                    nucacid=nuc_acid,
                    area=area
                )
                if row[2] != None:
                    nuc_acid.date = row[2]
                if row[4] != None:
                    nuc_acid.conc = row[4]
                if row[5] != None:
                    nuc_acid.vol_init = row[5]
                if row[6] != None:
                    nuc_acid.vol_remain = row[6]
                nuc_acid.notes = row[7]
                nuc_acid.save()
            # except Exception as e:
            #     print(e, row[1], row[-1])
        for row in rows2:
            try:
                if row[3] != None:
                    na_type = MigrateDump.get_na_type(row[3])
                    nuc_acid, _ = NucAcids.objects.get_or_create(name=row[1],na_type=na_type)
                else:
                    nuc_acid, _ = NucAcids.objects.get_or_create(name=row[1])
                if row[2] != None:
                    nuc_acid.date = row[2]
                if row[4] != None:
                    nuc_acid.conc = row[4]
                if row[5] != None:
                    nuc_acid.vol_init = row[5]
                if row[6] != None:
                    nuc_acid.vol_remain = row[6]
                nuc_acid.notes = row[7]
                nuc_acid.save()
            except Exception as e:
                print(e, row[1])
        for row in rows3:
            try:
                area = Areas.objects.get(name=row[-2])
                na = NucAcids.objects.get(name=row[-1])
                link = AREA_NA_LINK.objects.get_or_create(area=area, nucacid=na)
            except Exception as e:
                print(e,row[1],row[-1])

    @staticmethod
    def get_barcode(sl):
        try:
            files = SequencingFile.objects.filter(sequencing_file_set__sample_lib=sl)
            for file in files:
                # print(file.name)
                barcode = list(set(re.findall(r'[ATGC]{5,}', file.name)))[0]
                q = Q(Q(i5=barcode) | Q(i7=barcode))
                if barcode:
                    _barcode = Barcode.objects.filter(q)
                    if _barcode:
                        return _barcode[0]
            return None
        except:
            print(f"Barcode not found for {sl.name}")

    @staticmethod
    def register_barcode(row, sl):
        try:
            barcode= Barcode.objects.get(name=row[12].strip())
            sl.barcode = barcode
            sl.save()
        except:
            print(f"{row[12].strip()} Barcode not found for {sl.name}")


    @staticmethod
    def register_samplelib():
        sql = '''
                    SELECT * FROM na_sl_link l
                '''
        sql2 = '''
                    SELECT * FROM sample_lib order by name
                '''
        sql3 = '''
            SELECT l.*, n.name as nucacid, s.name as samplelib, s.name
            FROM na_sl_link l
            LEFT JOIN sample_lib s on l.sample_lib_id = s.id
            LEFT JOIN nuc_acids n on n.id = l.nucacid_id
        '''
        sql4 = '''
            SELECT name FROM sample_lib where barcode_id is Null
        '''
        rows = MigrateDump().cursor(sql)
        rows2 = MigrateDump().cursor(sql2)
        rows3 = MigrateDump().cursor(sql3)
        rows4 = MigrateDump().cursor(sql4)
        md = set([i[0] for i in rows4])
        db = set([i["name"] for i in SampleLib.objects.filter(barcode__isnull=True).values("name")])
        print(db-md)

        # for row in rows:
        #     try:
        #         nas = row[-1].split(',')
        #         sl,_ = SampleLib.objects.get_or_create(name=row[-2])
        #         for na in nas:
        #             nuc_acid = NucAcids.objects.get(name=na.strip())
        #             NA_SL_LINK.objects.get_or_create(sample_lib=sl, nucacid=nuc_acid)
        #     except Exception as e:
        #         print(e, nas)

        for row in rows2:
            try:
                sl, _ = SampleLib.objects.get_or_create(name=row[1].strip())
                if row[2]:
                    sl.date = row[2]
                sl.qubit = row[3] or 0
                sl.shear_volume = row[4] or 0
                sl.qpcr_conc = row[5] or 0
                sl.pcr_cycles = row[6] or 0
                sl.amount_in = row[7] or 0
                sl.amount_final = row[8] or 0
                sl.vol_init = row[9] or 0
                sl.vol_remain = row[10] or 0
                if row[11]:
                    sl.notes = row[11]
                else:
                    sl.notes = ""
                sl.save()
                if not " migration_dump" in sl.notes:
                    sl.notes = sl.notes + " migration_dump"
                sl.save()
                if row[12] != None:
                    MigrateDump.register_barcode(row, sl)
            except Exception as e:
                print(e, row[1],row[-3])


    @staticmethod
    def register_capturedlib():
        file = Path(Path(__file__).parent.parent / "uploads" / "sl-cl-match_from_AT_CD.csv")
        df = pd.read_csv(file)
        df = df.reset_index()  # make sure indexes pair with number of rows

        for index, row in df.iterrows():
            try:
                # print(row['sample_lib'], row['CL from Air Table'], row['CL from Consolidated Data'])
                sl = SampleLib.objects.get(name=row['sample_lib'])
                if not pd.isnull(row['CL from Consolidated Data']) and pd.isnull(row['CL from Air Table']):
                    cl, _ = CapturedLib.objects.get_or_create(name=row['CL from Consolidated Data'])
                    link, _ = SL_CL_LINK.objects.get_or_create(captured_lib=cl, sample_lib=sl)
                    # print("#"*100)
                elif not pd.isnull(row['CL from Air Table']):
                    for i in row['CL from Air Table'].split(","):
                        cl, _ = CapturedLib.objects.get_or_create(name=i)
                        link, _ = SL_CL_LINK.objects.get_or_create(captured_lib=cl, sample_lib=sl)
                        # print("-"*10)
                sls = SampleLib.objects.filter(name__startswith="FKP")
            except Exception as e:
                print(e, row)
        for sl in sls:
            cl = CapturedLib.objects.get(name="SGPC-04")
            link, _ = SL_CL_LINK.objects.get_or_create(captured_lib=cl, sample_lib=sl)

    @staticmethod
    def find_seq_runs_for_non_sl_cl_relation():
        file = Path(Path(__file__).parent.parent / "uploads" / "data-1722566158414.csv")
        df = pd.read_csv(file)
        df = df.reset_index()  # make sure indexes pair with number of rows
        file = Path(Path(__file__).parent.parent / "uploads" / "df_fq.csv")
        df_fq = pd.read_csv(file)
        df_fq = df_fq.reset_index()  # make sure indexes pair with number of rows

        for index, row in df.iterrows():
            try:
                sl = SampleLib.objects.get(name=row['sample_lib'])
                s = df_fq[df_fq['file'].str.contains(row['sample_lib'])]["path"].values[0]
                print(s.split('/')[1])
            except Exception as e:
                print(e)

    @staticmethod
    def register_captured_lib_and_so():

        # cursor_ucsf = MigrateDump.connection_ucsf()
        # sl_ucsf = SampleLib.objects.filter()
        # local = SampleLib.objects.using('local').filter().count()
        # print(sl_ucsf, local)
        for file_set in SequencingFileSet.objects.filter():
            try:
                sl_ucsf = SampleLib.objects.using('ucsf').get(name=file_set.sample_lib.name)
                file_set_ucsf = SequencingFileSet.objects.using('ucsf').get(prefix=file_set.prefix)
                file_set_ucsf.sample_lib = sl_ucsf
                file_set_ucsf.save()
                print("saved", sl_ucsf)
            except Exception as e:
                print(e, file_set)
        # for link in SL_CL_LINK.objects.filter():
        #     try:
        #         sl = SampleLib.objects.using('ucsf').get(name=link.sample_lib.name)
        #         cl = CapturedLib.objects.using("ucsf").get(name=link.captured_lib.name)
        #         SL_CL_LINK.objects.using("ucsf").create(sample_lib=sl, captured_lib=cl)
        #         print("created", sl, cl)
        #     except Exception as e:
        #         print(e)

        # # sample_libs_without_sl_cl_link = SampleLib.objects.filter(sl_cl_links__isnull=True).order_by('name')
        # capture_libs_without_cl_seql_link = CapturedLib.objects.filter(cl_seql_links__isnull=True).order_by("name")
        # sequencinglibs_without_seqruns  = SequencingLib.objects.annotate(
        #     num_runs=Count('sequencing_runs')
        # ).filter(num_runs=0).order_by('name')
        # # l = ["WGS-01",
        # #     "WGS-01_rerun",
        # #     ]
        # # m = [
        # #     "BCB022",
        # #     "BCB024",
        # #
        # # ]
        # # s = dict(zip(l,m))
        # # for k,v in s.items():
        # #     cl = CapturedLib.objects.get(name=k)
        # #     seqL = SequencingLib.objects.get(name=f'{v}_SeqL')
        # #     CL_SEQL_LINK.objects.get_or_create(captured_lib=cl, sequencing_lib=seqL)
        # for seqL in sequencinglibs_without_seqruns:
        #     print(seqL.name)
        #     # prefixes = ['CL']
        #     # # # Check if any string in the list starts with the prefix
        #     # if any(seqL.name.startswith(s) for s in prefixes):
        #     #     print(seqL.name)
        #     #     suffix = seqL.name.split("_")[1]
        #     #     seqrun,_ = SequencingRun.objects.get_or_create(name=f'CL_{suffix}')
        #     #     seqrun.sequencing_libs.add(seqL)

    @staticmethod
    def register_barcodes():
        rows = MigrateDump().cursor("SELECT name, barcode_id FROM sample_lib")
        for row in rows:
            try:
                if row[1] != "NaN":
                    sl = SampleLib.objects.get(name=row[0])
                    b_name = row[1].replace(".0","").strip()
                    barcode = Barcode.objects.get(name=b_name)
                    sl.barcode = barcode
                    sl.save()
            except Exception as e:
                print(e, row)



if __name__ == "__main__":
    # m = MigrateDump.register_patients()
    # m = MigrateDump.register_blocks()
    # m = MigrateDump.register_areas()
    # m = MigrateDump.register_nuc_acids()
    # m = MigrateDump.register_samplelib()
    # m = MigrateDump.register_capturedlib()
    m = MigrateDump.find_seq_runs_for_non_sl_cl_relation()
    # m = MigrateDump.register_captured_lib_and_so()
    print("===FIN===")
    # res = m.cursor("SELECT * FROM patients")
