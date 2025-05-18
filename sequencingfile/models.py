import re
import os, logging
import json
from django.db import models
from django.db.models import Q, Count
from projects.utils import get_user_projects
from sequencingrun.models import SequencingRun
from samplelib.models import SampleLib
from django.core.exceptions import ObjectDoesNotExist
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
django.setup()

from django.conf import settings

logger = logging.getLogger("file-tree")


class SequencingFileSet(models.Model):
    set_id = models.AutoField(primary_key=True)
    sample_lib = models.ForeignKey("samplelib.SampleLib", blank=True, null=True, on_delete=models.SET_NULL, related_name="sequencing_file_sets")
    sequencing_run = models.ForeignKey("sequencingrun.SequencingRun", blank=True, null=True, on_delete=models.SET_NULL, related_name="sequencing_file_sets")
    prefix = models.CharField(max_length=250, unique=True) #"Yurif_DNA_GGCTAC"
    path = models.CharField(max_length=1000, blank=True, null=True)
    date_added = models.DateTimeField(blank=True, null=True, auto_now_add=True)


    class Meta:
        db_table = "sequencing_file_set"

    def __str__(self):
        return self.prefix

    @classmethod
    def generate_prefix(cls, file_name):
        try:
            match = re.match(r'.*[-_]([ACTG]{6,8})[-_]', file_name)
            prefix = None
            file_type = None

            lower_name = file_name.lower()
            # FASTQ files
            if "fastq" in lower_name:
                file_type = "fastq"
                if "_l0" in lower_name:
                    prefix = file_name.split("_L0")[0]
                elif "_001" in file_name:
                    prefix = file_name.split("_001")[0]
            # BAM variations
            elif ".sorted" in lower_name:
                file_type = "bam"
                prefix = file_name.split(".sorted")[0]
            elif ".sort" in lower_name:
                file_type = "bam"
                prefix = file_name.split(".sort")[0]
            elif ".removedupes" in lower_name:
                file_type = "bam"
                prefix = file_name.split(".removedupes")[0]
            elif ".recal" in lower_name:
                file_type = "bam"
                prefix = file_name.split(".recal")[0]
            elif "deduplicated.realign.bam" in lower_name:
                file_type = "bam"
                prefix = file_name.split(".deduplicated.realign.bam")[0]
            # BAI index
            elif file_name.endswith(".bai"):
                file_type = "bai"
                prefix = file_name.rsplit(".", 1)[0]
            # generic BAM
            elif file_name.endswith(".bam"):
                file_type = "bam"
                prefix = file_name.rsplit(".", 1)[0]

            # Override prefix if barcode found
            if match:
                dna = match.group(1)
                prefix = file_name.split(dna)[0] + dna

            # Fallback: filename without extension
            if prefix is None:
                prefix = os.path.splitext(file_name)[0]

            # Create or fetch the file set
            # file_set, created = cls.objects.get_or_create(prefix=prefix)
            # file_set.sample_lib = sample_lib
            # file_set.sequencing_run = seq_run
            # file_set.path = path
            # file_set.save()

            return prefix, file_type
        except Exception as e:
            print(f"Error generating file set for {file_name}: {e}")
            return None, None

    @staticmethod
    def find_sample(file_name):
        """
        Extract sample name from FASTQ/BAM/BAI filename and return matching SampleLib.
        """
        try:
            match = re.match(r"^(.*?)(?:_S|\.)", file_name)
            if match and re.search(r"\b(bam|bai)\b", file_name.lower()):
                return SampleLib.objects.get(name=match.group(1))
        except SampleLib.DoesNotExist:
            print(f"Sample not found {file_name}")
        return None

    @staticmethod
    def find_seqrun(path):
        """
        Parse sequencing run name from path and return matching SequencingRun.
        """
        try:
            sr_name = path.split("/")[1]
            return SequencingRun.objects.get(name=sr_name)
        except Exception:
            print(f"Seq Run not found {path}")
        return None

    @classmethod
    def get_file_set(cls, seq_run, sample_lib):
        """
        Retrieve a SequencingFileSet matching the given run and sample.
        """
        try:
            return cls.objects.get(sequencing_run=seq_run, sample_lib=sample_lib)
        except cls.DoesNotExist:
            print(f"SequencingFileSet not found {seq_run}, {sample_lib}")
            return None

    def query_by_args(self, user, **kwargs):

        def _get_authorizated_queryset():
            '''
            Users can access to some entities depend on their authorize. While the user having admin role can access to all things,
            technicians or researchers can access own projects and other entities related to it.
            '''
            queryset = SequencingFileSet.objects.all().annotate(num_sequencing_files=Count('sequencing_files', distinct=True))

            if not user.is_superuser:
                return queryset.filter(
                    sample_lib__na_sl_links__nucacid__area_na_links__area__block__block_projects__in=get_user_projects(user)
                )

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
            return "_initial:" in search_value and search_value.split("_initial:")[1] != "null"

        try:
            ORDER_COLUMN_CHOICES = {
                "0": "set_id",
                "1": "prefix",
                "2": "path",
                "5": "date_added",
            }
            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
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
            if is_initial:
                if search_value["model"] == "sequencing_run":
                    queryset = queryset.filter(
                        Q(sequencing_run__id=search_value["id"])
                    )
                else:
                    queryset = queryset.filter(
                        Q(sequencing_files__file_id=search_value["id"])
                    )
            elif search_value:
                queryset = queryset.filter(
                    Q(prefix__icontains=search_value) |
                    Q(path__icontains=search_value)
                )

            count = queryset.count()
            queryset = queryset.order_by(order_column)[start:start + length]
            # queryset = queryset[start:start + length]
            return {
                'items': queryset,
                'count': count,
                'total': total,
                'draw': draw
            }
        except Exception as e:
            print(str(e))
            raise


class SequencingFile(models.Model):
    FILE_TYPES = (
        ("fastq", "Fastq File"),
        ("bam", "Bam File"),
        ("bai", "Bam Bai File"),
    )
    file_id = models.AutoField(primary_key=True)
    sequencing_file_set = models.ForeignKey(SequencingFileSet, blank=True, null=True, on_delete=models.SET_NULL, related_name="sequencing_files")
    name = models.CharField(max_length=500, unique=True, verbose_name="File Name")
    checksum = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=10, choices=FILE_TYPES, blank=True, null=True)
    date_added = models.DateTimeField(blank=True, null=True, auto_now_add=True)


    class Meta:
        db_table = "sequencing_file"

    def __str__(self):
        return self.name

    @property
    def file_info(self):
        return {
            "file": self.name,
            "checksum": self.checksum,
        }

    @classmethod
    def get_with_file_set(cls, file_name: str, path: str):
        try:
            seq_file = cls.objects.get(name=file_name)
            fs = seq_file.sequencing_file_set
            if fs and fs.path != path:
                fs.path = path.replace(str(settings.SEQUENCING_FILES_SOURCE_DIRECTORY),"")
                # fs.save()
                logger.info("*")

            return seq_file, fs
        except ObjectDoesNotExist:
            logger.info(f"ObjectDoesNotExist: {file_name}, path {path.replace(str(settings.SEQUENCING_FILES_SOURCE_DIRECTORY),'')}")
            sample_lib = SequencingFileSet.find_sample(file_name)
            seq_run = SequencingFileSet.find_seqrun(path)
            prefix, file_type = SequencingFileSet.generate_prefix(file_name=file_name)
            # seq_file = cls.objects.create(
            #     sequencing_file_set=fs,
            #     name=file_name,
            #     type=file_type
            # )
            logger.info(f"Created new file: {file_name}, set={prefix}, "
                        f"type={file_type},  sample_lib={sample_lib},  seq_run={seq_run}")
            return seq_file, fs

    def query_by_args(self, user, **kwargs):

        def _get_authorizated_queryset():
            return SequencingFile.objects.all()

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
            return "_initial:" in search_value and search_value.split("_initial:")[1] != "null"

        try:
            ORDER_COLUMN_CHOICES = {
                "0": "file_id",
                "1": "name",
            }
            draw = int(kwargs.get('draw', None)[0])
            length = int(kwargs.get('length', None)[0])
            start = int(kwargs.get('start', None)[0])
            search_value = kwargs.get('search[value]', None)[0]
            order_column = kwargs.get('order[0][column]', None)[0]
            order = kwargs.get('order[0][dir]', None)[0]

            order_column = ORDER_COLUMN_CHOICES[order_column]
            if order == 'desc':
                order_column = '-' + order_column

            queryset = _get_authorizated_queryset()
            total = queryset.count()
            is_initial = _is_initial_value(search_value)
            search_value = _parse_value(search_value)

            if is_initial:
                if search_value["model"] == "sample_lib":
                    queryset = queryset.filter(
                        Q(sequencing_file_set__sample_lib__id=search_value["id"])
                    )
                elif search_value["model"] == "sequencingfileset":
                    queryset = queryset.filter(
                        Q(sequencing_file_set__set_id=search_value["id"])
                    )
                else:
                    queryset = queryset.filter(
                        Q(sequencing_file_set__set_id=search_value)
                    )
            elif search_value:
                queryset = queryset.filter(
                    Q(name__icontains=search_value) |
                    Q(sequencing_file_set__path__icontains=search_value) |
                    Q(sequencing_file_set__prefix__icontains=search_value)
                )

            count = queryset.count()
            queryset = queryset.order_by(order_column)[start:start + length]
            # queryset = queryset[start:start + length]
            return {
                'items': queryset,
                'count': count,
                'total': total,
                'draw': draw
            }
        except Exception as e:
            print(str(e))
            raise
