import os
import csv
from django.conf import settings
from analysisrun.models import AnalysisRun
from cns.models import Cns
from variant.models import VariantCall
from variant.models import VariantFile
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import pylab
import base64
from PIL import Image
from io import BytesIO

BASE_PATH = settings.VARIANT_FILES_SOURCE_DIRECTORY

def handle_variant_file(ar_name, folder):
    folder_path = find_folders(ar_name, folder)
    if folder_path:
        cns_files=find_cns_files(folder_path)
        return cns_files
    else:
        raise Exception("Folder not found")

def find_folders(ar_name, folder):
    first_level_dirs = next(os.walk(BASE_PATH))[1]
    if not any(ar_name in dir_name for dir_name in first_level_dirs):
        raise ValueError(f"Error: '{ar_name}' not found in any first-level directories of {BASE_PATH}")

    return os.path.join(BASE_PATH, ar_name, folder)

def find_cns_files(folder):
    cns_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".cns") and ".bintest" not in file and ".call" not in file:
                cns_files.append(os.path.join(root, file))
    return cns_files

def parse_cns_file(file_path, ar_name):
    try:
        analysis_run = AnalysisRun.objects.get(name=ar_name)
        file_name = file_path.split['/'][-1]

        variant_file = VariantFile.objects.get_or_create(name=file_name, directory=file_path)
        created_objects_count = 0

        sample_lib = file_name.split(".")[1]
        sequencing_run = file_name.split(".")[0]
        # with open(file_path, "r") as f:
        #     reader = csv.DictReader(f)
        df = pd.read_csv(file_path, index_col=False, sep='\t')
        for index, row in df.iterrows():
            # Check if the Cns object already exists
            if not Cns.objects.filter(
                sample_lib=sample_lib,
                sequencing_run=sequencing_run,
                variant_file=file_path,
                analysis_run=analysis_run,
                chromosome=row["chromosome"],
                start=int(row["start"]),
                end=int(row["end"]),
            ).exists():

                def get_float_value(value, default=0.0):
                    try:
                        return float(value)
                    except ValueError:
                        return default

                depth = get_float_value(row["depth"])
                ci_hi = get_float_value(row["ci_hi"])
                ci_lo = get_float_value(row["ci_lo"])
                cn = get_float_value(row.get("cn", 0.0))
                log2 = get_float_value(row["log2"])
                p_bintest = get_float_value(row.get("p_bintest", 0.0))
                p_ttest = get_float_value(row.get("p_ttest", 0.0))
                probes = get_float_value(row["probes"])
                weight = get_float_value(row["weight"])

                Cns.objects.create(
                    sample_lib=sample_lib,
                    sequencing_run=sequencing_run,
                    variant_file=file_path,
                    analysis_run=analysis_run,
                    chromosome=row["chromosome"],
                    start=int(row["start"]),
                    end=int(row["end"]),
                    gene=row["gene"],
                    depth=depth,
                    ci_hi=ci_hi,
                    ci_lo=ci_lo,
                    cn=cn,
                    log2=log2,
                    p_bintest=p_bintest,
                    p_ttest=p_ttest,
                    probes=probes,
                    weight=weight,
                )

                created_objects_count += 1

        return created_objects_count
    except AnalysisRun.DoesNotExist:
        print(f"AnalysisRun with name {ar_name} does not exist")
    except Exception as e:
        print(f"Error parsing file: {e}")

def generate_graph(ar_name,file_path):
 # CSV verilerini okuma
    df = pd.read_csv(file_path)

    # Örneğin, sadece 'chr11' kromozomuna ait verileri filtreleyelim
    df_subset = df[df['chromosome'] == 'chr11']

    # Belirli örnekleri seçelim
    sample_subset = df_subset['start'].unique()[:5]  # İlk 5 örnek
    df_subset = df_subset[df_subset['start'].isin(sample_subset)]

    # Plot the limited subset
    plt.figure(figsize=(10, 6))

    for sample in sample_subset:
        sample_data = df_subset[df_subset['start'] == sample]
        plt.plot(sample_data['start'], sample_data['log2'], label=sample)

    plt.xlabel('Genomic Position')
    plt.ylabel('Log2 Ratio')
    plt.title('Chromosome 11 Segments for Identified Samples')
    plt.legend()

    buffer = BytesIO()
    canvas = pylab.get_current_fig_manager().canvas
    canvas.draw()
    pilImage = Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    pilImage.save(buffer, "PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")
