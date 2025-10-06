import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
django.setup()
from django.conf import settings
import pandas as pd
from variant.models import VariantFile
import logging
from gene.models import Gene
from migration.variants_import import get_sample_lib, get_sequencing_run
from areas.models import Area
from areatype.models import AreaType
from cns.models import Cns
from analysisrun.models import AnalysisRun


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
    df.apply(lambda row: register_files(row), axis=1)

    pass

def create_csn(row, file):
    print(file)
    try:
        csn = Cns.objects.create(
            sample_lib=get_sample_lib(file.name),
            sequencing_run=get_sequencing_run(file.name),
            variant_file=file,
            analysis_run=AnalysisRun.objects.get(name="AR_ALL"),
            chromosome=row['chromosome'],
            start=row['start'],
            end=row['end'],
            gene=row['gene'][:499],
            depth=row['depth'],
            ci_hi=row.get('ci_hi', 0),
            ci_lo=row.get('ci_lo', 0),
            cn=row.get('cn', 0),
            log2=row['log2'],
            p_bintest=row.get('p_bintest', 0),
            p_ttest=row.get('p_ttest', 0),
            probes=row['probes'],
            weight=row['weight']
        )
    except Exception as e:
        print(e)

def import_csn_calls():
    Cns.objects.filter(variant_file__name__icontains='FKP').delete()
    for file in VariantFile.objects.filter(type='cns', directory__icontains='hg38_ProcessedData', name__icontains="FKP"):
        try:
            file_path = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA,file.directory, file.name)
            df = pd.read_csv(file_path, index_col=False, sep='\t')
            df.apply(lambda row: create_csn(row, file), axis=1)
        except:
            print("error", file_path, file)
    print("%^&"*100, "finished")

def create_area_types(row):
    if not AreaType.objects.filter(name=row['area_type']):
        area_type = AreaType.objects.create(
            name=row['area_type'],
            value=row['area_type']
        )
    else:
        area_type = AreaType.objects.get(name=row['area_type'])
    area = Area.objects.get(id=row['ar_id'])
    area.area_type = area_type
    area.save()

def import_area_types():
    SEQUENCING_FILES_SOURCE_DIRECTORY = os.path.join(settings.SMB_DIRECTORY_SEQUENCINGDATA, "ProcessedData")
    file_path = os.path.join(SEQUENCING_FILES_SOURCE_DIRECTORY, "areas.csv")
    df = pd.read_csv(file_path, index_col=False)
    df.apply(lambda row: create_area_types(row), axis=1)


    print("%^&"*100, "finished")


import os


def get_directory_size(directory_path):
    total_size = 0

    # Walk through the directory and its subdirectories
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                # Add the size of the file to the total size
                total_size += os.path.getsize(file_path)
            except FileNotFoundError:
                # In case the file is deleted before we get its size
                pass

    return total_size


def human_readable_size(size_in_bytes):
    # Convert bytes to a human-readable format (KB, MB, GB, etc.)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024


if __name__ == "__main__":
    folder_path = input("Enter the path of the folder: ")
    size_in_bytes = get_directory_size(folder_path)
    print(f"Total size of '{folder_path}' is: {human_readable_size(size_in_bytes)}")

