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


if __name__ == "__main__":
    m = MigrateDump.register_patients()
    print(m)
    # res = m.cursor("SELECT * FROM patients")