from django.db import models

class SampleQC(models.Model):
    sample_lib = models.ForeignKey("samplelib.SampleLib", on_delete=models.CASCADE, related_name='qc_metrics')
    analysis_run = models.ForeignKey("analysisrun.AnalysisRun", on_delete=models.CASCADE, related_name='qc_metrics')
    sequencing_run = models.ForeignKey("sequencingrun.SequencingRun", on_delete=models.CASCADE, related_name="sequencingrun_cns", blank=True, null=True)
    # Duplicate metrics
    unpaired_reads_examined = models.BigIntegerField(null=True, blank=True)
    read_pairs_examined = models.BigIntegerField(null=True, blank=True)
    secondary_or_supplementary_rds = models.BigIntegerField(null=True, blank=True)
    unmapped_reads = models.BigIntegerField(null=True, blank=True)
    unpaired_read_duplicates = models.BigIntegerField(null=True, blank=True)
    read_pair_duplicates = models.BigIntegerField(null=True, blank=True)
    read_pair_optical_duplicates = models.BigIntegerField(null=True, blank=True)
    percent_duplication = models.FloatField(null=True, blank=True)
    estimated_library_size = models.FloatField(null=True, blank=True)
    # Hs metrics
    pct_off_bait = models.FloatField(null=True, blank=True)
    mean_bait_coverage = models.FloatField(null=True, blank=True)
    mean_target_coverage = models.FloatField(null=True, blank=True)
    median_target_coverage = models.FloatField(null=True, blank=True)
    pct_target_bases_1x = models.FloatField(null=True, blank=True)
    pct_target_bases_2x = models.FloatField(null=True, blank=True)
    pct_target_bases_10x = models.FloatField(null=True, blank=True)
    pct_target_bases_20x = models.FloatField(null=True, blank=True)
    pct_target_bases_30x = models.FloatField(null=True, blank=True)
    pct_target_bases_40x = models.FloatField(null=True, blank=True)
    pct_target_bases_50x = models.FloatField(null=True, blank=True)
    pct_target_bases_100x = models.FloatField(null=True, blank=True)
    at_dropout = models.FloatField(null=True, blank=True)
    gc_dropout = models.FloatField(null=True, blank=True)
    # Insert size metrics
    median_insert_size = models.IntegerField(null=True, blank=True)
    mode_insert_size = models.IntegerField(null=True, blank=True)
    mean_insert_size = models.FloatField(null=True, blank=True)

    # Path to histogram PDF
    insert_size_histogram_path = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('sample_lib', 'analysis_run')
        db_table = 'sample_qc'

    def __str__(self):
        return f"QC metrics for {self.sample_lib} - {self.analysis_run}"
