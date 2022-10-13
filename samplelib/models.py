from django.db import models

class Barcode(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Name")
    i5 = models.CharField(max_length=10, unique=True, verbose_name="I5")
    i5 = models.CharField(max_length=10, unique=True, verbose_name="I7")

    class Meta:
        db_table = "barcode"

class SampleLib(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Name")
    barcode = models.ForeignKey(Barcode, on_delete=models.CASCADE, verbose_name="Barcode")
    date = models.DateField(default=date.today, verbose_name="Date")
    method = models.ForeignKey("method.Method",related_name="sample_libs",on_delete=models.CASCADE, verbose_name="Method")
    te_vol = models.FloatField(blank=True, null=True, verbose_name="Te Volume")
    input_amount = models.FloatField(blank=True, null=True, verbose_name="Input Amount")
    vol_init = models.FloatField(blank=True, null=True, verbose_name="Volume Initialize")
    vol_remain = models.FloatField(blank=True, null=True, verbose_name="Volume Remain")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    class Meta:
        db_table = "sample_lib"

class NA_SL_LINK(models.Model):
    nucacid = models.ForeignKey("libprep.NucAcids",on_delete=models.CASCADE, verbose_name="Nucleic Acid")
    sample_lib = models.ForeignKey(SampleLib, on_delete=models.CASCADE, verbose_name="Sample Library")
    input_vol = models.FloatField(default=0, verbose_name="Te Volume")
    input_amount = models.FloatField(default=0, verbose_name="Input Amount")

    class Meta:
        db_table = "na_sl_link"
