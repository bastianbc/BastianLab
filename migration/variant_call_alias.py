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




def check_alias():
    for vc in VariantCall.objects.filter():
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


def generate_variant():
    for vc in VariantCall.objects.filter():
        cv_all = CVariant.objects.filter(g_variant__variant_call=vc)
        for cv in cv_all:
            pv = cv.p_variants.first()
            if pv:
                if cv.is_alias == True and cv.is_gene_detail == False:
                    variant = f"{pv.name_meta}({cv.nm_id})"
                if cv.is_alias == False and cv.is_gene_detail == True:
                    variant = f"{cv.gene_detail}"
        vc.variant_meta = variant
        vc.save()
        print(f"variant saved: {variant}")







if __name__ == "__main__":
    print("start")
    generate_variant()
    print("end")
