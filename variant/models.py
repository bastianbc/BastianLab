from django.db import models

class VariantCall(models.Model):
    sample_lib = models.ForeignKey("samplelib.SampleLib", on_delete=models.CASCADE, related_name="variant_calls")
    sequencing_run = models.ForeignKey("sequencingrun.SequencingRun", on_delete=models.CASCADE, related_name="variant_calls")
    coverage = models.IntegerField(default=0)
    # run_analysis = models.ForeignKey(RunAnalysis, on_delete=models.CASCADE, related_name="variant_calls")
    log2r = models.FloatField(default=0.0)
    caller = models.CharField(max_length=30)
    normal_sl = models.ForeignKey("samplelib.SampleLib", on_delete=models.CASCADE, related_name="variant_calls_for_normal")
    label = models.CharField(max_length=30)
    ref_read = models.IntegerField(default=0)
    alt_read = models.IntegerField(default=0)

    class Meta:
        db_table = "variant_call"

class GVariant(models.Model):
    hg = models.IntegerField(default=0)
    chrom = models.CharField(max_length=30)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    ref = models.CharField(max_length=30)
    alt = models.CharField(max_length=30)
    avsnp150 = models.CharField(max_length=30)

    class Meta:
        db_table = "g_variant"

class CVariant(models.Model):
    g_variant = models.ForeignKey(GVariant, on_delete=models.CASCADE, related_name="c_variants")
    gene = models.CharField(max_length=30)
    nm_id = models.CharField(max_length=30)
    c_var = models.CharField(max_length=30)
    exon = models.CharField(max_length=30)
    func = models.CharField(max_length=30)
    gene_detail = models.CharField(max_length=30)

    class Meta:
        db_table = "c_variant"

class PVariant(models.Model):
    c_variant = models.ForeignKey(CVariant, on_delete=models.CASCADE, related_name="p_variants")
    p_var_ref = models.CharField(max_length=30)
    p_var_pos = models.CharField(max_length=30)
    p_var_alt = models.CharField(max_length=30)

    class Meta:
        db_table = "p_variant"
