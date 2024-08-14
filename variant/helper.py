import pandas as pd
from django.db import transaction
from .models import VariantCall, GVariant, CVariant, PVariant
import re

def get_caller(filename):
    caller_match = re.match(r'.*?(\w+)_Final', filename)
    return caller_match.group(1) if caller_match else None

def parse_p_var(p_var):
    match = re.match(r'p\.([A-Za-z])(\d+)([A-Za-z])', p_var)
    if match:
        return match.group(1), match.group(2), match.group(3)  # ref, pos, alt
    return None, None, None

def get_log2r():
    """
    Note: We need to write some code for this later
    """
    return None

def get_normal_sample_lib(sample_lib):
    """
    This relates to any SL from a normal area for Tumor/Normal sequencing
    (i.e. where the DNA from the tumor AND the normal DNA was sequenced).
    By definition, no normal exists for Tumor only sequencing
    """
    from samplelib.models import SampleLib

    return SampleLib.objects.filter(
            na_sl_links__nucacid__na_type='dna',
            na_sl_links__nucacid__area_na_links__area__area_type='normal',
            na_sl_links__nucacid__na_sl_links__sample_lib=sample_lib
        ).exclude(pk=sample_lib.pk).values_list('name', flat=True).distinct()

def get_hg(filename):
    """
    AM2-063.HS_Final.annovar.hg19_multianno_Filtered.txt
    [sample_lib.name].[Caller name]_Final.annovar.[assembly]_multianno_Filtered.txt
    """
    match = re.search(r'\.hg\d+_', filename)
    if match:
        assembly = match.group(0)[1:-1]  # İlk ve son karakterleri ('.' ve '_') çıkarıyoruz
        return assembly
    return None

def get_sample_lib(filename):
    """
    AM2-063.HS_Final.annovar.hg19_multianno_Filtered.txt
    [sample_lib.name].[Caller name]_Final.annovar.[assembly]_multianno_Filtered.txt
    """
    match = re.match(r'^[^.]+', filename)
    if match:
        return match.group(0)
    return None

def get_sequencing_run(filename):
    return None

def get_analysis_run(name):
    return AnalysisRun.objects.get(name=name)

def create_c_and_p_variants(g_variant, aachange, func, gene_detail):
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
def variant_file_parser(file, analysis_run_name):
    df = pd.read_csv(file, sep='\t')

    sample_lib = get_sample_lib(file.name)

    for _, row in df.iterrows():
        variant_call = VariantCall.objects.create(
            run_analysis=get_analysis_run(analysis_run_name),
            sample_lib=sample_lib,
            sequencing_run=get_sequencing_run(file.name),
            coverage=row['Depth'],
            log2r=get_log2r(),
            caller=get_caller(file.name),
            normal_sl=get_normal_sample_lib(sample_lib),
            label="",
            ref_read=row['Ref_reads'],
            alt_read=row['Alt_reads'],
        )

        g_variant = GVariant.objects.create(
            variant_call=variant_call,
            hg=get_hg(file.name),
            chrom=row['Chr'],
            start=row['Start'],
            end=row['End'],
            ref=row['Ref'],
            alt=row['Alt'],
            avsnp150=row['avsnp150']
        )

        create_c_and_p_variants(
            g_variant=g_variant,
            aachange=row['AAChange.refGene'],
            func=row['Func.refGene'],
            gene_detail=row['GeneDetail.refGene']
        )
