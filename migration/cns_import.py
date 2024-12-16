import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
django.setup()
from sequencingrun.models import SequencingRun
from django.conf import settings
import pandas as pd
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from variant.models import VariantCall, GVariant, CVariant, PVariant, VariantFile
from analysisrun.models import AnalysisRun
from samplelib.models import SampleLib
import re
import logging
from pathlib import Path
from gene.models import Gene


logger = logging.getLogger("file")





def import_csn_files():
    SEQUENCING_FILES_SOURCE_DIRECTORY = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA, "ProcessedData")
    file = os.path.join(SEQUENCING_FILES_SOURCE_DIRECTORY, "cns_files.csv")
    df = pd.read_csv(file, index_col=False)
    df = df.reset_index()
    columns = set()
    for index, row in df.iterrows():
        file_path = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA, row['Dir'], row['File'])
        with open(file_path, "r", encoding="ascii") as f:
            first_line = f.readline().strip().split("\t")
            columns.update(set(first_line))
            print(f"First line: {first_line}")

    # df.apply(create_genes, axis=1)
    pass


if __name__ == "__main__":
    print("start")
    import_csn_files()
    print("end")

