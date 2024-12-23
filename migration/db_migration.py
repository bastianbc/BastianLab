from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps
from gene.models import Gene

class Command(BaseCommand):
    help = "Copy VariantCall and related data from labdb to labdbproduction using Django ORM, including CNS."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data copy for VariantCall, related models, and CNS...")

        # Get the models
        VariantCall = apps.get_model("variant", "VariantCall")
        GVariant = apps.get_model("variant", "GVariant")
        CVariant = apps.get_model("variant", "CVariant")
        PVariant = apps.get_model("variant", "PVariant")
        VariantFile = apps.get_model("variant", "VariantFile")
        Cns = apps.get_model("variant", "Cns")
        SampleLib = apps.get_model("samplelib", "SampleLib")
        SequencingRun = apps.get_model("sequencingrun", "SequencingRun")
        AnalysisRun = apps.get_model("analysisrun", "AnalysisRun")

        # Fetch VariantCalls from the source database
        variant_calls = VariantCall.objects.using(source_db).all()

        with transaction.atomic(using=target_db):
            for variant_call in variant_calls:
                # Get related SampleLib, SequencingRun, VariantFile, and AnalysisRun in the target database
                sample_lib = SampleLib.objects.using(target_db).filter(name=variant_call.sample_lib.name).first() if variant_call.sample_lib else None
                sequencing_run = SequencingRun.objects.using(target_db).filter(name=variant_call.sequencing_run.name).first() if variant_call.sequencing_run else None
                variant_file = VariantFile.objects.using(target_db).filter(name=variant_call.variant_file.name).first() if variant_call.variant_file else None
                analysis_run = AnalysisRun.objects.using(target_db).filter(name=variant_call.analysis_run.name).first()

                # Skip if AnalysisRun is not found
                if not analysis_run:
                    self.stdout.write(f"AnalysisRun {variant_call.analysis_run.id} not found, skipping VariantCall {variant_call.id}.")
                    continue

                # Create the VariantCall in the target database
                new_variant_call = VariantCall.objects.using(target_db).create(
                    sample_lib=sample_lib,
                    sequencing_run=sequencing_run,
                    variant_file=variant_file,
                    coverage=variant_call.coverage,
                    analysis_run=analysis_run,
                    log2r=variant_call.log2r,
                    caller=variant_call.caller,
                    normal_sl=sample_lib,
                    label=variant_call.label,
                    ref_read=variant_call.ref_read,
                    alt_read=variant_call.alt_read,
                )
                self.stdout.write(f"Created VariantCall {variant_call.id}.")

                # Copy related GVariant
                g_variants = GVariant.objects.using(source_db).filter(variant_call=variant_call)
                for g_variant in g_variants:
                    new_g_variant = GVariant.objects.using(target_db).create(
                        variant_call=new_variant_call,
                        hg=g_variant.hg,
                        chrom=g_variant.chrom,
                        start=g_variant.start,
                        end=g_variant.end,
                        ref=g_variant.ref,
                        alt=g_variant.alt,
                        avsnp150=g_variant.avsnp150,
                    )
                    self.stdout.write(f"Created GVariant {g_variant.id} for VariantCall {variant_call.id}.")

                    # Copy related CVariant
                    c_variants = CVariant.objects.using(source_db).filter(g_variant=g_variant)
                    for c_variant in c_variants:
                        gene = Gene.objects.filter(nm_canonical=c_variant.gene.nm_id).first()
                        new_c_variant = CVariant.objects.using(target_db).create(
                            g_variant=new_g_variant,
                            gene=gene if gene else None,
                            nm_id=c_variant.nm_id,
                            c_var=c_variant.c_var,
                            exon=c_variant.exon,
                            func=c_variant.func,
                            gene_detail=c_variant.gene_detail,
                        )
                        self.stdout.write(f"Created CVariant {c_variant.id} for GVariant {g_variant.id}.")

                        # Copy related PVariant
                        p_variants = PVariant.objects.using(source_db).filter(c_variant=c_variant)
                        for p_variant in p_variants:
                            PVariant.objects.using(target_db).create(
                                c_variant=new_c_variant,
                                start=p_variant.start,
                                end=p_variant.end,
                                reference_residues=p_variant.reference_residues,
                                inserted_residues=p_variant.inserted_residues,
                                change_type=p_variant.change_type,
                                name_meta=p_variant.name_meta,
                            )
                            self.stdout.write(f"Created PVariant {p_variant.id} for CVariant {c_variant.id}.")

            # Copy CNS data
            cns_records = Cns.objects.using(source_db).all()
            for cns in cns_records:
                # Get related SampleLib, SequencingRun, and VariantFile in the target database
                sample_lib = SampleLib.objects.using(target_db).filter(name=cns.sample_lib.name).first() if cns.sample_lib else None
                sequencing_run = SequencingRun.objects.using(target_db).filter(name=cns.sequencing_run.name).first() if cns.sequencing_run else None
                variant_file = VariantFile.objects.using(target_db).filter(name=cns.variant_file.name).first() if cns.variant_file else None

                # Create the CNS object in the target database
                Cns.objects.using(target_db).create(
                    sample_lib=sample_lib,
                    sequencing_run=sequencing_run,
                    variant_file=variant_file,
                    chromosome=cns.chromosome,
                    start=cns.start,
                    end=cns.end,
                    gene=cns.gene,
                    depth=cns.depth,
                    ci_hi=cns.ci_hi,
                    ci_lo=cns.ci_lo,
                    cn=cns.cn,
                    log2=cns.log2,
                    p_bintest=cns.p_bintest,
                    p_ttest=cns.p_ttest,
                    probes=cns.probes,
                    weight=cns.weight,
                )
                self.stdout.write(f"Created CNS record for SampleLib {sample_lib.name if sample_lib else 'N/A'}.")

        self.stdout.write("Data copy for VariantCall, related models, and CNS completed.")



def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



