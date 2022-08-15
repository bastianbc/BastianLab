from django.db import models
from datetime import date

class Projects(models.Model):

    BORIS = 'BB'
    IWEI = 'IY'
    PI_CHOICES = [
        (BORIS, 'Boris Bastian'),
        (IWEI, 'Iwei Yeh'),
    ]
    name = models.CharField(max_length=100, blank=False, null=False)
    abbreviation = models.CharField(max_length=6, blank=False, null=False, unique=True, default='XY')
    pi = models.CharField(max_length=2, choices=PI_CHOICES, default=BORIS, blank=True, null=True)
    speedtype = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    date_start = models.DateField(blank=True, null=True, default=date.today)
    pr_id = models.AutoField(primary_key=True)


    class Meta:
        managed = True
        db_table = 'projects'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
    
    # def get_absolute_url(self):
    #         return reverse('patient-update', kwargs={'pk': self.pk})

    def __str__(self):
       return self.name
