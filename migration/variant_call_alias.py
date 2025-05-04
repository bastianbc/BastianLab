import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
django.setup()
from sequencingrun.models import SequencingRun
from django.conf import settings
import pandas as pd
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from variant.models import VariantCall, GVariant, CVariant, PVariant, VariantFile
from analysisrun.models import AnalysisRun
from samplelib.models import SampleLib
import re
import logging
from pathlib import Path
from gene.models import Gene


logger = logging.getLogger("file")




def generate_variant():
    for vc in VariantCall.objects.filter(variant_file__name="BCB013.SGLP-0418.MT2_Final.annovar.hg19_multianno_Filtered.txt"):
        cv_all = CVariant.objects.filter(g_variant__variant_call=vc)
        for cv in cv_all:

            if not cv.gene_detail or not cv.gene or not cv.gene.nm_canonical:
                print(f"Skipping due to missing gene_detail or gene data for CVariant ID {cv.id}")
                continue

            parts = cv.gene_detail.split(':')
            if len(parts) < 2:
                print(f"Skipping malformed gene_detail: '{cv.gene_detail}' for CVariant ID {cv.id}")
                continue

            # Extract nm_id if available
            nm_id = parts[1].strip()

            # Defensive comparison
            is_alias = False
            if nm_id and cv.gene.nm_canonical and nm_id.lower() == cv.gene.nm_canonical.lower():
                is_alias = True

            cv.is_alias = is_alias
            cv.save()
            print(f"Saved")



    pass


if __name__ == "__main__":
    print("start")
    generate_variant()
    print("end")
