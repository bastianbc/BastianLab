from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.validators import validate_name_contains_space
from django.db.models import Q, Count, Value, CharField, Subquery, OuterRef, IntegerField, Case, When
from django.db.models.functions import Coalesce
from django.utils.crypto import get_random_string
import json
from projects.utils import get_user_projects
from variant.models import VariantCounts


class Block(models.Model):
    P_STAGE_TYPES = (
        ("Tis", "Tis"),
        ("T1a", "T1a"),
        ("T1b", "T1b"),
        ("T2a", "T2a"),
        ("T2b", "T2b"),
        ("T3a", "T3a"),
        ("T3b", "T3b"),
        ("T4a", "T4a"),
        ("T4b", "T4b"),
    )

    PRIM_TYPES = (
         ("primary","Primary"),
         ("metastasis","Metastasis"),
    )

    SUBTYPE_CHOICES = (
        ("low-csd", "Low CSD"),
        ("high-csd", "High CSD"),
        ("acral", "Acral"),
        ("mucosal", "Mucosal"),
        ("uveal", "Uveal"),
        ("desmoplastic", "Desmoplastic"),
        ("melanoma-ex-blue-nevus", "Melanoma Ex Blue Nevus"),
        ("melanoma-ex-congenital-nevus", "Melanoma Ex Congenital Nevus" ),
        ("conjunctival-melanoma", "Conjunctival Melanoma"),
        ("desmoplastic-melanoma", "Desmoplastic Melanoma"),
        ("nos", "NOS"),
    )

    FIXATION_CHOICES = (
        ("ffpe", "FFPE"),
        ("frozen" , "frozen"),
        ("ethanol", "ethanol"),
    )

    CSD_CHOICES = (
        ("0", "0"),
        ("1", "1"),
        ("1-", "1-"),
        ("1+", "1+"),
        ("2", "2"),
        ("2-", "2-"),
        ("2+", "2+"),
        ("3", "3"),
        ("3-", "3-"),
        ("3+", "3+"),

    )

    name = models.CharField(max_length=50, blank=True, null=False, unique=True)
    patient = models.ForeignKey('lab.Patient', on_delete=models.CASCADE, db_column='patient', blank=True, null=True, related_name="patient_blocks")
    # project = models.ForeignKey('projects.Projects', on_delete=models.DO_NOTHING, blank=True, null=True, related_name="project_blocks")
    age = models.FloatField(blank=True, null=True, validators=[
        MinValueValidator((0.1), message='Minimum age is 0.1 years'),
        MaxValueValidator((120), message='Maximum age is 120 years'),
        ])
    body_site = models.ForeignKey("body.Body", on_delete=models.CASCADE, blank=True, null=True)
    ulceration = models.BooleanField(blank=True, null=True)
    thickness = models.FloatField(blank=True, null=True, help_text="float field ex. 0.1", verbose_name="Tumor thickness [mm]")
    mitoses = models.IntegerField(blank=True, null=True, verbose_name="Mitoses [per mm2]")
    p_stage = models.CharField(max_length=10, choices=P_STAGE_TYPES, blank=True, null=True)
    csd_score = models.CharField(max_length=3, choices=CSD_CHOICES, blank=True, null=True)
    prim = models.CharField(max_length=10, choices=PRIM_TYPES, blank=True, null=True)
    subtype = models.CharField(max_length=120, blank=True, null=True, choices=SUBTYPE_CHOICES)
    slides = models.IntegerField(blank=True, null=True)
    slides_left = models.IntegerField(blank=True, null=True)
    fixation = models.CharField(max_length=100, blank=True, null=True, choices=FIXATION_CHOICES, default="ffpe")
    storage = models.CharField(max_length=50, blank=True, null=True)
    scan_number = models.CharField(max_length=200,blank=True, null=True)
    icd10 = models.CharField(max_length=8 ,blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True, verbose_name="Investigator notes")
    micro = models.TextField(blank=True, null=True)
    gross = models.TextField(blank=True, null=True)
    clinical = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    old_body_site = models.CharField(max_length=600,blank=True, null=True)

    path_note = models.TextField(blank=True, null=True)
    ip_dx = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'block'

    def __str__(self):
        return self.name

    def _generate_unique_id(self):
        return get_random_string(length=6)

    def save(self,*args,**kwargs):
        if not self.name:
            self.name = self._generate_unique_id()

        super().save(*args, **kwargs)

    def query_by_args(user, **kwargs):
        '''
        This is where the sorting and filtering functions of the datatables are executed.
        Parameters:
            user (obj): Active django user
            kwargs (dict): All parameters that the datatables used
        Returns:
            data (dict): Data that the user will see on the screen
        '''
        def _get_authorizated_queryset():
            '''
            Users can access to some entities depend on their authorize. While the user having admin role can access to all things,
            technicians or researchers can access own projects and other entities related to it.
            '''
            block_url_sq = BlockUrl.objects.order_by('id').values('url')[:1]

            queryset = (
                Block.objects
                .annotate(
                    num_areas=Count('block_areas', distinct=True),
                    project_num=Count('block_projects', distinct=True),
                    patient_num=Count('patient', distinct=True),
                    num_variants=Coalesce(
                        Subquery(
                            VariantCounts.objects
                            .filter(block_id=OuterRef('pk'))
                            .values('block_variant_count')[:1],
                            output_field=IntegerField(),
                        ),
                        Value(0),
                        output_field=IntegerField(),
                    ),

                    # <- add the global block url (first record)
                    block_url=Case(
                        When(
                            Q(scan_number__isnull=False) & ~Q(scan_number=""),
                            then=Subquery(block_url_sq),
                        ),
                        default=Value(None),
                        output_field=CharField(),
                    ),
                )
            )

            if not user.is_superuser:
                return queryset.filter(block_projects__in=get_user_projects(user))

            return queryset

        def _parse_value(search_value):
            '''
            When the datatables are to be filled with a certain data, the search function of datatables is used.
            The incoming parameter is parsed ve returned. If there is a initial value, the "search_value" has "_initial" prefix.
            Parameters:
                search_value (str): A string
            Returns:
                search_value (str): Parsed value
            '''
            if "_initial:" in search_value:
                return json.loads(search_value.split("_initial:")[1])
            return search_value

        def _is_initial_value(search_value):
            '''
            When the datatables are to be filled with a certain data, the search function of datatables is used.
            The incoming parameter is parsed ve returned. If there is a initial value, the "search_value" has "_initial" prefix.
            Parameters:
                search_value (str): A string
            Returns:
                is_initial (boolean): If there is a initial value, it is True
            '''
            return "_initial:" in search_value and search_value.split("_initial:")[1] != "null"

        def _filter_by_project(value):
            return queryset.filter(Q(block_projects=value))

        def _filter_by_patient(value):
            return queryset.filter(Q(patient__id=value))

        def _filter_by_area(value):
            return queryset.filter(Q(block_areas__id=value))

        def _filter_by_samplelib(value):
            return queryset.filter(Q(block_areas__area_na_links__nucacid__na_sl_links__sample_lib__id=value))

        try:
            ORDER_COLUMN_CHOICES = {
                "1":"id",
                "2":"name",
                "3":"project",
                "4":"patient",
                "5":"diagnosis",
                "6":"body_site",
                "7":"scan_number",
                "8":"num_areas",
                "9":"num_variants",
            }
            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            p_stage = kwargs.get('p_stage', None)[0]
            prim = kwargs.get('prim', None)[0]
            body_site = kwargs.get('body_site', None)[0]
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
            if p_stage:
                queryset = queryset.filter(
                    Q(p_stage=p_stage)
                )
            if prim:
                queryset = queryset.filter(
                    Q(prim=prim)
                )

            if body_site:
                queryset = queryset.filter(
                    Q(body_site__id=body_site)
                )
            if is_initial:
                if search_value["model"] == "project":
                    queryset = _filter_by_project(search_value["id"])
                elif search_value["model"] == "patient":
                    queryset = _filter_by_patient(search_value["id"])
                elif search_value["model"] == "samplelib":
                    queryset = _filter_by_samplelib(search_value["id"])
                elif search_value["model"] == "area":
                    queryset = _filter_by_area(search_value["id"])
            elif search_value:
                queryset = queryset.filter(
                        Q(name__icontains=search_value) |
                        Q(diagnosis__icontains=search_value) |
                        Q(gross__icontains=search_value)
                    )

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

    @staticmethod
    def get_block_url():
        return BlockUrl.objects.values("url").first()

class BlockUrl(models.Model):
    url = models.CharField(max_length=1000, blank=True, null=True, verbose_name="")

    class Meta:
        db_table = 'blockurl'
        managed = True
