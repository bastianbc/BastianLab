from django.db import models


class IpPatients(models.Model):
    pat_id = models.TextField(blank=False, null=False, unique=True, primary_key=True)
    race = models.TextField(blank=True, null=True)
    gender = models.TextField(blank=True, null=True)
    birth_year = models.IntegerField(blank=True, null=True)
    count = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'unipats'
        # indexes = [
        #     models.Index(fields=['pat_id',])
        #     ]



class Accessions(models.Model):
    patient = models.ForeignKey('IpPatients', on_delete=models.CASCADE)
    dept_number = models.TextField(blank=False, null=False, unique=True, primary_key=True)
    pathologist = models.TextField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    dept_code = models.TextField(blank=True, null=True)
    specimen_count = models.IntegerField(blank=True, null=True)
    clinical = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'accessions'
        # indexes = [
        #     models.Index(fields=['dept_number',]),
        #     models.Index(fields=['pat_id',]),
        #     ]

class Parts(models.Model):
    accession = models.ForeignKey('Accessions',to_field='dept_number', on_delete=models.CASCADE)
    block_id=models.TextField(blank=False, null=False, unique=True, primary_key=True)
    site_code = models.TextField(blank=True, null=True)
    dx_text = models.TextField(blank=True, null=True)
    clinical = models.TextField(blank=True, null=True)
    gross = models.TextField(blank=True, null=True)
    micro = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    cpt_code = models.TextField(blank=True, null=True)
    dx_code = models.TextField(blank=True, null=True)
    icd9 = models.TextField(blank=True, null=True)
    site_text = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'parts'
        # indexes = [
        #     models.Index(fields=['block_id',])
        #     ]

class Melanomas(models.Model):
    part=models.OneToOneField('Parts', on_delete=models.CASCADE, primary_key=True)
    p_stage = models.TextField(blank=True, null=True)
    thickness = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    ulceration = models.BooleanField(blank=True, null=True)
    mitoses = models.IntegerField(blank=True, null=True)
    prim = models.TextField(blank=True, null=True)
    subtype = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'melanomas'
        # indexes = [
        #     model
        #s.Index(fields=['dept_number',])
        #     ]


class Outcomes(models.Model):
    ccr_patient_id = models.TextField(blank=True, null=True, unique=True,)
    patient = models.OneToOneField('IpPatients', on_delete=models.CASCADE, primary_key=True)
    c_stage = models.TextField(blank=True, null=True)
    cause_of_death = models.TextField(blank=True, null=True)
    nodes_sampled = models.TextField(blank=True, null=True)
    nodes_positive = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    ccr_datestat_decode = models.TextField(blank=True, null=True)
    months_survived = models.TextField(blank=True, null=True)
    date_last_contact_or_death = models.TextField(blank=True, null=True)
    vital_status = models.TextField(blank=True, null=True)


    class Meta:
        managed = True
        db_table = 'outcomes'
        # indexes = [
        #     models.Index(fields=['ippatient',])
        #     ]
