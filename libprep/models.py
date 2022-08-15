from django.db import models
from lab.models import Areas
from datetime import date


class NucAcids(models.Model):
    old_na_id = models.CharField(max_length=50, blank=True, null=True)
    old_area_id = models.CharField(max_length=50, blank=True, null=True)
    na_type = models.CharField(max_length=20, blank=True, null=True)
    date_extr = models.DateField(blank=True, null=True, default=date.today)
    method = models.CharField(max_length=50, blank=True, null=True)
    qubit = models.FloatField(blank=True, null=True)
    volume = models.IntegerField(blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)
    re_ext = models.FloatField(blank=True, null=True)
    total_ext = models.FloatField(blank=True, null=True)
    na_sheared = models.FloatField(blank=True, null=True)
    shearing_vol = models.FloatField(blank=True, null=True)
    te_vol = models.FloatField(blank=True, null=True)
    sl_id = models.CharField(max_length=50, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    projects = models.CharField(max_length=100, blank=True, null=True)
    area = models.ForeignKey(Areas, on_delete=models.SET_NULL, db_column='area', blank=True, null=True)
    nu_id = models.AutoField(primary_key=True)

    class Meta:
        managed = True
        db_table = 'nuc_acids'

    # @property
    # def calc_amount(self):
    #     # calculates the amount
    #     return self.qubit * self.volume
    # def save(self, *args, **kwargs): 
    #     #Following lines set qubit and volume to 0 if they are None.
    #     kwargs.get('qubit',0)
    #     kwargs.get('volume',0)
    #     self.amount = self.qubit * self.volume
    #     super(NucAcids, self).save(*args, **kwargs)

class SampleLib(models.Model):
    sl_id = models.CharField(max_length=50, blank=True, null=True)
    na_id = models.CharField(max_length=50, blank=True, null=True)
    pre_pcr = models.IntegerField(blank=True, null=True)
    post_lib_qubit = models.FloatField(blank=True, null=True)
    post_lib_qpcr = models.FloatField(blank=True, null=True)
    vol_lib = models.IntegerField(blank=True, null=True)
    lp_dna = models.FloatField(blank=True, null=True)
    re_lp_amount = models.FloatField(blank=True, null=True)
    re_lp2_amount = models.FloatField(blank=True, null=True)
    total_lp_dna = models.FloatField(blank=True, null=True)
    chosen_for_capt = models.CharField(max_length=30, blank=True, null=True)
    input_dna = models.FloatField(blank=True, null=True)
    input_vol = models.FloatField(blank=True, null=True)
    post_pcr = models.IntegerField(blank=True, null=True)
    barcode_id = models.CharField(max_length=50, blank=True, null=True)
    prep_date = models.DateField(blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    project = models.CharField(max_length=50, blank=True, null=True)
    nuc_acid = models.ForeignKey(NucAcids, on_delete=models.CASCADE, db_column='nuc_acid', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sample_lib'

