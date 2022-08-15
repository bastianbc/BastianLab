from django.db import models

class IpUnipatsTest(models.Model):
    pat_id = models.TextField(blank=False, null=False, unique=True, primary_key=True)
    name = models.TextField(blank=True, null=True)
    dob = models.TextField(blank=True, null=True)
    ssn = models.TextField(blank=True, null=True)
    mrn = models.TextField(blank=True, null=True)
    gender = models.TextField(blank=True, null=True)
    birth_year = models.IntegerField(blank=True, null=True)
    count = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ip_unipatstest'
        # indexes = [
        #     models.Index(fields=['pat_id',])
        #     ]



class IpAccessionsTest(models.Model):
    pat_id = models.ForeignKey('IpUnipatsTest', on_delete=models.CASCADE)
    dept_number = models.TextField(blank=False, null=False, unique=True, primary_key=True)
    date_collected = models.DateField(blank=True, null=True)
    date_received = models.DateField(blank=True, null=True)
    pathologist = models.TextField(blank=True, null=True)
    pat_age = models.IntegerField(blank=True, null=True)
    ref_phy = models.IntegerField(blank=True, null=True)
    pat_recordnumber = models.TextField(blank=True, null=True)
    dept_code = models.TextField(blank=True, null=True)
    specimens = models.IntegerField(blank=True, null=True)
    clinical = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ip_accessionstest'
        # indexes = [
        #     models.Index(fields=['dept_number',]),
        #     models.Index(fields=['pat_id',]),
        #     ]

# class IpBlocks(models.Model):
#     dept_number = models.ForeignKey('IpAccessions',to_field='dept_number', on_delete=models.CASCADE)
#     spec_id = models.TextField(blank=True, null=True)
#     block_id=models.TextField(blank=False, null=False, unique=True, primary_key=True)
#     site_code = models.TextField(blank=True, null=True)
#     dx_text = models.TextField(blank=True, null=True)
#     clinical = models.TextField(blank=True, null=True)
#     gross = models.TextField(blank=True, null=True)
#     micro = models.TextField(blank=True, null=True)
#     note = models.TextField(blank=True, null=True)
#     cpt_code = models.TextField(blank=True, null=True)
#     dx_code = models.TextField(blank=True, null=True)
#     icd9 = models.TextField(blank=True, null=True)
#     spec_type = models.TextField(blank=True, null=True)
#     site_text = models.TextField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'ip_blocks'
#         # indexes = [
#         #     models.Index(fields=['dept_number',])
#         #     ]

# class IpMelanomas(models.Model):
#     dept_number = models.TextField(blank=True, null=True)
#     spec_id = models.TextField(blank=True, null=True)
#     block_id=models.ForeignKey('IpBlocks',to_field='block_id', on_delete=models.CASCADE)
#     p_stage = models.TextField(blank=True, null=True)
#     note = models.TextField(blank=True, null=True)
#     thickness = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     ulceration = models.BooleanField(blank=True, null=True)
#     mitoses = models.IntegerField(blank=True, null=True)
#     prim = models.TextField(blank=True, null=True)
#     subtype = models.TextField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'ip_melanomas'
#         # indexes = [
#         #     models.Index(fields=['dept_number',])
#         #     ]


# class IpCcr(models.Model):
#     ccr_patient_id = models.TextField(blank=False, null=False, unique=True, primary_key=True)
#     dept_number = models.ForeignKey('IpAccessions',to_field='dept_number', on_delete=models.CASCADE)
#     race1_decode = models.TextField(blank=True, null=True)
#     sumstage_decode = models.TextField(blank=True, null=True)
#     match_to_ucsf = models.TextField(blank=True, null=True)
#     recurrence = models.TextField(blank=True, null=True)
#     ccr_number_of_invasive_melanomas = models.TextField(blank=True, null=True)
#     case_control = models.TextField(blank=True, null=True)
#     cause_of_death_decode = models.TextField(blank=True, null=True)
#     survival_group = models.TextField(blank=True, null=True)
#     pt_code = models.TextField(blank=True, null=True)
#     ct_code = models.TextField(blank=True, null=True)
#     cn_code = models.TextField(blank=True, null=True)
#     cm_code = models.TextField(blank=True, null=True)
#     ctnm_stage = models.TextField(blank=True, null=True)
#     pt_code2 = models.TextField(blank=True, null=True)
#     pn_code = models.TextField(blank=True, null=True)
#     pm_code = models.TextField(blank=True, null=True)
#     ptnm_stage = models.TextField(blank=True, null=True)
#     xnodetu_decode = models.TextField(blank=True, null=True)
#     pnodetu_decode = models.TextField(blank=True, null=True)
#     ccr_tustat_decode = models.TextField(blank=True, null=True)
#     ccr_datestat_decode = models.TextField(blank=True, null=True)
#     surv_mon_act_decode = models.TextField(blank=True, null=True)
#     date_last_contact_or_death = models.TextField(blank=True, null=True)
#     vital_status = models.TextField(blank=True, null=True)
#     cause_of_death_decode2 = models.TextField(blank=True, null=True)
#     date_last_tumor_status_ucsf = models.TextField(blank=True, null=True)
#     tumor_status_ucsf = models.TextField(blank=True, null=True)
#     date_recurrence = models.TextField(blank=True, null=True)
#     type_recurrence = models.TextField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'ip_ccr'
#         # indexes = [
#         #     models.Index(fields=['dept_number',])
#         #     ]
