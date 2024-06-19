import pandas as pd
from django.db import transaction
from .models import VariantCall, GVariant, CVariant, PVariant, RunAnalysis
import re

def extract_caller_from_filename(filename):
    caller_match = re.match(r'.*?(\w+)_Final', filename)
    return caller_match.group(1) if caller_match else None

def parse_p_var(p_var):
    match = re.match(r'p\.([A-Za-z])(\d+)([A-Za-z])', p_var)
    if match:
        return match.group(1), match.group(2), match.group(3)  # ref, pos, alt
    return None, None, None

def get_log2r():
    return None

def get_normal_sample_lib(sample_lib):
    return None

def get_hg():
    return None

def get_sample_lib():
    return None

def get_sequencing_run():
    return None

def get_run_analysis():
    return None

def parse_and_create_variants(g_variant, aachange, func, gene_detail):
    entries = aachange.split(',')
    for entry in entries:
        gene, nm_id, exon, c_var, p_var = entry.split(':')

        # Create CVariant instance
        c_variant = CVariant.objects.create(
            g_variant=g_variant,
            gene=gene,
            nm_id=nm_id,
            exon=exon,
            c_var=c_var,
            func=func,
            gene_detail=gene_detail
        )

        # Create PVariant instance if p_var is present
        if p_var:
            p_ref, p_pos, p_alt = parse_p_var(p_var)
            PVariant.objects.create(
                c_variant=c_variant,
                ref=p_ref,
                pos=p_pos,
                alt=p_alt
            )

@transaction.atomic
def load_data_to_db(df,filename):
    run_analysis = get_run_analysis()
    sample_lib = get_sample_lib()
    sequencing_run = get_sequencing_run()
    caller = extract_caller_from_filename(filename)
    
    for _, row in df.iterrows():
        variant_call = VariantCall.objects.create(
            run_analysis=run_analysis,
            sample_lib=sample_lib,
            sequencing_run=sequencing_run,
            coverage=row['Depth'],
            log2r=get_log2r(),
            caller=get_caller(),
            normal_sl=get_normal_sample_lib(),
            label="",
            ref_read=row['Ref_reads'],
            alt_read=row['Alt_reads'],
        )

        g_variant = GVariant.objects.create(
            variant_call=variant_call,
            hg=get_hg(),
            chrom=row['Chr'],
            start=row['Start'],
            end=row['End'],
            ref=row['Ref'],
            alt=row['Alt'],
            avsnp150=row['avsnp150']
        )

        # Parse AAChange.refGene and create variants
        parse_and_create_variants(
            g_variant=g_variant,
            aachange=row['AAChange.refGene'],
            func=row['Func.refGene'],
            gene_detail=row['GeneDetail.refGene']
        )
