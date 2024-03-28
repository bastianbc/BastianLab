import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test1.settings')
django.setup()
from django.shortcuts import get_object_or_404

from django.shortcuts import render, redirect
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
import uuid
import psycopg2
from psycopg2 import OperationalError
import getpass


class MigrateDump():
    database_name = "migration_dump"
    database_user = "cbagci"
    database_password = 'Deneme-12345'
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
        for x in Patients.RACE_TYPES:
            if value.lower() == x[1].lower():
                return x[0]
        return 7

    @staticmethod
    def register_patients():
        rows = MigrateDump().cursor("SELECT * FROM patients")
        # print(Patients.objects.all().count())
        for row in rows:
            try:
                # print(row)
                # print(row[0])
                patient, created = Patients.objects.get_or_create(
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
                # patient.pa_id = row[7]
                patient.pat_ip_id = row[9] or ""
                patient.save()
                # patient = get_or_create(Patients, pat_id=row[0])
                # print(patient)
            except Exception as e:
                print(row[0], e)

    @staticmethod
    def get_collection(value):
        for x in Blocks.COLLECTION_CHOICES:
            if value.lower() == x[1].lower():
                return x[0]
        return Blocks.SCRAPE

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
                # qs = Projects.objects.filter(abbreviation__startswith=l[1])
                # if qs.exists():
                #     return "%s-%d" % (l[1],len(qs))
                return l[1]

        return ''.join(random.choices(string.digits, k=5))

    @staticmethod
    def register_blocks():
        rows = MigrateDump().cursor("SELECT * FROM blocks")
        # print(Patients.objects.all().count())
        for row in rows:
            try:
                # print(row[-4])
                patient = Patients.objects.get(pat_id=row[-4])
                block, created = Blocks.objects.get_or_create(
                    name=row[1]
                )
                block.patient = patient
                block.age = row[2]
                # block.body_site =
                block.ulceration = row[3]
                block.thickness = row[4]
                block.mitoses = row[5]
                block.p_stage = row[6] if row[6] is not None else None
                if row[7] != None:
                    block.prim = row[7].lower() if row[7].lower() in [item[0].lower() for item in Blocks.PRIM_TYPES] else None
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
                if row[22] != None:
                    block.collection = MigrateDump.get_collection(row[22])
                block.path_note = row[23]
                block.ip_dx = row[24]
                if row[-3] != None:
                    project = Projects.objects.filter(name=row[-3]).first()
                    if not project:
                        project = Projects.objects.create(name=row[-3], abbreviation=MigrateDump.get_abbreviation(row[-3]))
                    block.project = project
                block.save()
            except Exception as e:
                print(e, row[-3])

    @staticmethod
    def get_area_type(value):
        for x in Areas.AREA_TYPE_TYPES:
            if value.lower() == x[1].lower():
                return x[0]
        return None

    @staticmethod
    def register_areas():
        sql = '''
        SELECT a.*, l.*, b.name as block, b.bl_id FROM AREAS a
        RIGHT JOIN block_area_link l on a.ar_id=l.area
        RIGHT JOIN blocks b on l.block = b.bl_id
        '''
        sql2 = '''SELECT * FROM AREAS '''
        # rows = MigrateDump().cursor(sql2)
        rows2 = MigrateDump().cursor(sql2)
        # for row in rows:
        #     try:
        #         if row[0] != None:
        #             block = Blocks.objects.get(name=row[-1].strip())
        #             # print(block)
        #             # Areas.objects.get(name=row[1])
        #             if block:
        #                 area, _ = Areas.objects.get_or_create(name=row[1], block=block)
        #             # area.block = block
        #             if row[2] != None:
        #                 area.area_type = MigrateDump.get_area_type(row[2])
        #             area.image = row[4]
        #             area.notes = row[5]
                    # area.save()
        #         # print(row)
        #     except ObjectDoesNotExist:
        #         print(row[-1])
        #         block = Blocks.objects.get(name="BB"+row[-1].strip())
        #         area = Areas.objects.get(name=row[1])
        #         area.block = block
        #         area.save()
        #     except Exception as e:
        #         print(e,row[1], row[-1])
        for row in rows2:
            try:
                area = Areas.objects.get(name=row[1])
                if row[2] != None:
                    area.area_type = MigrateDump.get_area_type(row[2])
                area.image = row[4]
                area.notes = row[5]
                area.save()
                # if not area:
                #     print(row[1], " - ", row[-1])
                #     block = Blocks.objects.get(name=row[-1].strip())
                #     # if "," in row[-1]:
                #     #     for i in row[-1].split(","):
                #     #         print(i)
                #     #         block = Blocks.objects.get(name=i)
                #     area, _ = Areas.objects.get_or_create(name=row[1],block=block)
                #     if row[2] != None:
                #         area.area_type = MigrateDump.get_area_type(row[2])
                #     area.image = row[4]
                #     area.notes = row[5]
                #     if row[2] != None:
                #         area.area_type = MigrateDump.get_area_type(row[2])
                #     area.image = row[4]
                #     area.notes = row[5]
                #     area.save()
                # else:
                #     if "," in row[-1]:
                #         for i in row[-1].split(","):
                #             # print("%%%",i)
                #             block = Blocks.objects.get(name=i)
                #             area = Areas.objects.get(name=row[1])
                #             area.block=block
                #             if row[2] != None:
                #                 area.area_type = MigrateDump.get_area_type(row[2])
                #             area.image = row[4]
                #             area.notes = row[5]
                #             area.save()
                #     else:
                #         # print("iii")
                #         block = MigrateDump.get_or_none(Blocks, name=row[-1])
                #         if not block:
                #             block = MigrateDump.get_or_none(Blocks, name="BB"+row[-1])
                #         if block:
                #             area = Areas.objects.get(name=row[1])
                #             area.block = block
                #             if row[2] != None:
                #                 area.area_type = MigrateDump.get_area_type(row[2])
                #             area.image = row[4]
                #             area.notes = row[5]
                #             area.save()
            except Exception as e:
                print("{} area:{}, block{}".format(e, row[1], row[-1]))

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
            LEFT JOIN area_na_link nl on nl.area_id = a.ar_id
            LEFT JOIN nuc_acids n on n.nu_id = nl.nucacid_id
            order by n.name
        '''
        sql2 = '''
            SELECT * FROM nuc_acids
        '''
        sql3 = '''
            SELECT nl.* ,
            a.name as area, 
            n.name as nuc_acid FROM area_na_link nl
            LEFT JOIN nuc_acids n on n.nu_id = nl.nucacid_id
            LEFT JOIN areas a on a.ar_id = nl.area_id
            WHERE nucacid_id is not NULL AND
            area_id is not NULL
        '''
        rows = MigrateDump().cursor(sql)
        rows2 = MigrateDump().cursor(sql2)
        rows3 = MigrateDump().cursor(sql3)
        # for row in rows:
        #     try:
        #         # print(row)
        #         if row[-1] != None:
        #             area = Areas.objects.get(name=row[-1])
        #         if row[3] != None:
        #             na_type = MigrateDump.get_na_type(row[3])
        #             nuc_acid, _ = NucAcids.objects.get_or_create(name=row[1],na_type=na_type)
        #         else:
        #             nuc_acid, _ = NucAcids.objects.get_or_create(name=row[1])
        #         link = AREA_NA_LINK.objects.get_or_create(
        #             nucacid=nuc_acid,
        #             area=area
        #         )
        #         if row[2] != None:
        #             nuc_acid.date = row[2]
        #         if row[4] != None:
        #             nuc_acid.conc = row[4]
        #         if row[5] != None:
        #             nuc_acid.vol_init = row[5]
        #         if row[6] != None:
        #             nuc_acid.vol_remain = row[6]
        #         nuc_acid.notes = row[7]
        #         nuc_acid.save()
        #     except Exception as e:
        #         print(e, row[1], row[-1])
        # for row in rows2:
        #     try:
        #         if row[3] != None:
        #             na_type = MigrateDump.get_na_type(row[3])
        #             nuc_acid, _ = NucAcids.objects.get_or_create(name=row[1],na_type=na_type)
        #         else:
        #             nuc_acid, _ = NucAcids.objects.get_or_create(name=row[1])
        #         if row[2] != None:
        #             nuc_acid.date = row[2]
        #         if row[4] != None:
        #             nuc_acid.conc = row[4]
        #         if row[5] != None:
        #             nuc_acid.vol_init = row[5]
        #         if row[6] != None:
        #             nuc_acid.vol_remain = row[6]
        #         nuc_acid.notes = row[7]
        #         nuc_acid.save()
        #     except Exception as e:
        #         print(e, row[1])
        for row in rows3:
            try:
                if row[-2]:
                    area = Areas.objects.get(name=row[-2])
                else:
                    print("else")
                    area = Areas.objects.get(name=row[-4])
                na = NucAcids.objects.get(name=row[-1])
                link = AREA_NA_LINK.objects.get_or_create(area=area, nucacid=na)
            except Exception as e:
                print(e,row[1],row[-1])

    @staticmethod
    def get_barcode(sl):
        try:
            file = SequencingFile.objects.filter(sequencing_file_set__sample_lib=sl).first()
            print(file)
            barcode = re.search("^[ATGC-]+$", file.name)
            print(barcode)
            q = Q(Q(i5=barcode) | Q(i7=barcode))
            barcode = Barcode.objects.filter(q)
            print(barcode)
        except:
            # print(f"Barcode not found for {sl.name}")
            pass

    @staticmethod
    def register_samplelib():
        # print(SampleLib.objects.filter(name__startswith="T12-"))
        # for sl in SampleLib.objects.filter(name__startswith="T12-"):
        #     name = sl.name
        #     sl.name = name.replace("-","_")
        #     sl.save()
        sql = '''
                    SELECT n.*, nl.*, a.name FROM AREAS a
                    LEFT JOIN area_na_link nl on nl.area_id = a.ar_id
                    LEFT JOIN nuc_acids n on n.nu_id = nl.nucacid_id
                    order by n.name
                '''
        sql2 = '''
                    SELECT * FROM sample_lib
                '''
        sql3 = '''
                    SELECT l.*, n.name as nucacid, s.name as samplelib, s.na_name
                    FROM na_sl_link l
                    LEFT JOIN sample_lib s on l.sample_lib_id = s.id
                    LEFT JOIN nuc_acids n on n.nu_id = l.nucacid_id
                '''
        rows = MigrateDump().cursor(sql)
        rows2 = MigrateDump().cursor(sql2)
        rows3 = MigrateDump().cursor(sql3)
        for row in rows2:
            try:
                sl = SampleLib.objects.get(name=row[1].strip())
                MigrateDump.get_barcode(sl)
                # if row[2]:
                #     sl.date = row[2]
                # sl.qubit = row[3] or 0
                # sl.shear_volume = row[4] or 0
                # sl.qpcr_conc = row[5] or 0
                # sl.pcr_cycles = row[6] or 0
                # sl.amount_in = row[7] or 0
                # sl.amount_final = row[8] or 0
                # sl.vol_init = row[9] or 0
                # sl.vol_remain = row[10] or 0
                # sl.notes = row[1]
                #
                # sl.save()
            except Exception as e:
                print(e, row[1])
        # for row in rows3:
        #     try:
        #         sl = SampleLib.objects.get(name=row[-2])
        #         na = NucAcids.objects.get(name=row[-3])
        #         link, _ = NA_SL_LINK.objects.get_or_create(sample_lib=sl, nucacid=na)
        #         link.input_vol = row[1] or 0
        #         link.input_amount = row[2] or 0
        #         link.save()
        #     except Exception as e:
        #         print(e)

if __name__ == "__main__":
    # m = MigrateDump.register_areas()
    # m = MigrateDump.register_nuc_acids()
    m = MigrateDump.register_samplelib()
    print("===FIN===")
    # res = m.cursor("SELECT * FROM patients")