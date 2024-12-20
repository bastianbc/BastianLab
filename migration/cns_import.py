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


def canonical():
    updated_aachange = []
    SEQUENCING_FILES_SOURCE_DIRECTORY = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA, "ProcessedData")
    # file = os.path.join(SEQUENCING_FILES_SOURCE_DIRECTORY, "canonical_errors.csv")
    file = os.path.join(SEQUENCING_FILES_SOURCE_DIRECTORY, "canonical_errors_with_AAChange.csv")
    df = pd.read_csv(file, index_col=False)
    df = df.reset_index()
    df['AAChange.refGene'] = ''
    for index, row in df.iterrows():
        # print(row['File'])
        var_file = VariantFile.objects.filter(name__icontains=row['File']).first()
        df_var = pd.read_csv(os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA, var_file.directory, var_file.name), sep='\t')
        pattern = f"{row['Gene']}.*{row['NM_ID']}"

        filtered = df_var[df_var['AAChange.refGene'].str.contains(pattern, regex=True)]['AAChange.refGene'].tolist()[0]
        find = []
        for entry in filtered.split(","):
            gene, nm_id, exon, c_var, p_var = entry.split(':')
            gene = Gene.objects.filter(nm_canonical=nm_id)
            # print(gene)
            if gene:
                find.append(True)
            else:
                find.append(False)
            if any(find):
                df.at[index, 'AAChange.refGene'] = "Good"
            else:
                df.at[index, 'AAChange.refGene'] = filtered

    good_genes = df.loc[df['AAChange.refGene'] == 'Good', 'Gene'].unique()

    # Remove all rows with matching Gene values
    df = df[~df['Gene'].isin(good_genes)]
    # df.to_csv(os.path.join(SEQUENCING_FILES_SOURCE_DIRECTORY, "canonical_errors_with_AAChange.csv"))
    df.to_csv(os.path.join(SEQUENCING_FILES_SOURCE_DIRECTORY, "canonical_errors_with_AAChange_2.csv"))

def register_files(row):
    VariantFile.objects.create(
        name=row['File'],
        directory=row['Dir'],
        call=False,
        type="cns",
    )


def import_csn_files():
    SEQUENCING_FILES_SOURCE_DIRECTORY = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA, "ProcessedData")
    file = os.path.join(SEQUENCING_FILES_SOURCE_DIRECTORY, "cns_files.csv")
    df = pd.read_csv(file, index_col=False)
    df = df.reset_index()
    columns = set()
    df.apply(lambda row: register_files(row), axis=1)
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
    # import_csn_files()
    canonical()
    print("end")

