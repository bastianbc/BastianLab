from django.db import models
from projects.utils import get_user_projects
from django.db.models import Q
import json
from datetime import datetime

class SampleQC(models.Model):
    FILE_TYPES = [
        ('dup_metrics', 'dup'),
        ('hs_metrics', "hs"),
        ('insert_size_metrics', "insert_size")
    ]
    sample_lib = models.ForeignKey("samplelib.SampleLib", on_delete=models.CASCADE, related_name='qc_metrics', blank=True, null=True)
    analysis_run = models.ForeignKey("analysisrun.AnalysisRun", on_delete=models.CASCADE, related_name='qc_metrics')
    sequencing_run = models.ForeignKey("sequencingrun.SequencingRun", on_delete=models.CASCADE, related_name="qc_metrics", blank=True, null=True)
    variant_file = models.ForeignKey("variant.VariantFile", on_delete=models.CASCADE, related_name="qc_metrics", blank=True, null=True)
    type = models.CharField(max_length=20, choices=FILE_TYPES, blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, verbose_name="Date")
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
    insert_size_histogram = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        # unique_together = ('sample_lib', 'analysis_run')
        db_table = 'sample_qc'

    def __str__(self):
        return f"QC metrics for {self.sample_lib} - {self.analysis_run}"

    def query_by_args(self, user, **kwargs):
        def _get_authorizated_queryset():
            queryset = SampleQC.objects.all()
            if not user.is_superuser:
                return queryset.filter(
                    sample_lib__na_sl_links__nucacid__area_na_links__area__block__block_projects__in=get_user_projects(user)
                )

            return queryset

        def _parse_value(search_value):
            if "_initial:" in search_value:
                return json.loads(search_value.split("_initial:")[1])

            return search_value

        def _is_initial_value(search_value):
            return "_initial:" in search_value and search_value.split("_initial:")[1] != "null"

        try:
            ORDER_COLUMN_CHOICES = {
                '0': 'id',
                '1': 'sample_lib',
                '2': 'sequencing_run',
                '4': 'analysisrun',
                '5': 'insert_size_histogram',
            }

            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            sample_lib_filter = kwargs.get('sample_lib', None)[0]
            analysis_run_filter = kwargs.get('analysis_run', None)[0]
            sequencing_run_filter = kwargs.get('sequencing_run', None)[0]
            variant_file_filter = kwargs.get('variant_file', None)[0]
            type_filter = kwargs.get('type', None)[0]

            order_column = kwargs.get('order[0][column]', None)[0]
            order = kwargs.get('order[0][dir]', None)[0]
            order_column = ORDER_COLUMN_CHOICES[order_column]
            # django orm '-' -> desc
            if order == 'desc':
                order_column = '-' + order_column

            queryset = _get_authorizated_queryset()

            total = queryset.count()

            is_initial = _is_initial_value(search_value)
            search_value = _parse_value(search_value)

            if search_value:
                queryset = queryset.filter(
                    Q(id__icontains=search_value) |
                    Q(sample_lib__name__icontains=search_value) |
                    Q(sequencing_run__name__icontains=search_value)
                )


            if sequencing_run_filter:
                queryset = queryset.filter(Q(sequencing_run__id=sequencing_run_filter))

            if sample_lib_filter:
                queryset = queryset.filter(Q(sample_lib__id=sample_lib_filter))

            if variant_file_filter:
                queryset = queryset.filter(Q(variant_file__id=variant_file_filter))

            if type_filter:
                queryset = queryset.filter(Q(type=type_filter))

            if analysis_run_filter:
                queryset = queryset.filter(Q(analysisrun__id=analysis_run_filter))



            count = queryset.count()
            queryset = queryset.order_by(order_column)[start:start + length]
            return {
                'items': queryset,
                'count': count,
                'total': total,
                'draw': draw
            }
        except Exception as e:
            print(str(e))
            raise