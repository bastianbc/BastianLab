import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
django.setup()
from variant.models import VariantCall, CVariant, PVariant
import logging
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
        variant=""
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

def generate_variant_2():
    calls = VariantCall.objects.filter()

    for vc in calls:
        print(vc.sample_lib.name)
        variant_list=[]
        aliases_list=[]
        for pv in PVariant.objects.filter(c_variant__g_variant__variant_call=vc):
            if pv.c_variant.is_alias==True and pv.c_variant.is_gene_detail==False:
                variant_list.append(f'{pv.name_meta}({pv.c_variant.nm_id})')
            elif pv.is_alias==True and pv.c_variant.is_gene_detail==True:
                variant_list.append(f'{pv.c_variant.gene_detail}')
            if pv.c_variant.is_alias==False and pv.c_variant.is_gene_detail==False:
                aliases_list.append(f'{pv.name_meta}({pv.c_variant.nm_id})')
            elif pv.is_alias==False and pv.c_variant.is_gene_detail==True:
                aliases_list.append(f'{pv.c_variant.gene_detail}')
        vc.variant_meta = ", ".join(variant_list)
        vc.alias_meta = ", ".join(aliases_list)
        vc.save()
    pass


import csv
from analysisrun.models import VariantFile
from analysisrun.models import AnalysisRun
from pathlib import Path


def restore_variant_files():
    with open(Path(__file__).parent / "variant_file_dump.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            VariantFile.objects.update_or_create(
                analysis_run=AnalysisRun.objects.get(id=2),
                name=row['name'],
                directory=row['directory'],
                defaults={
                    'type': row['type'],
                    'call': row.get('call', False),
                    'status': row.get('status', 'pending'),
                }
            )





# if __name__ == "__main__":
#     print("start")
#     generate_variant_2()
#     print("end")
