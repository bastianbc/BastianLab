import os
import csv
from django.conf import settings
from .models import AnalysisRun
from cns.models import Cns
from variant.models import VariantCall

# /Volumes/sequencingdata/ProcessedData/Analysis.tumor-only/Small_Gene_Panel/2-Oct-24/cnv/output/BCB002.NMLP-001/BCB002.NMLP-001.Tumor_dedup_BSQR.cns
BASE_PATH = settings.VARIANT_FILES_SOURCE_DIRECTORY

def handle_variant_file(ar_name, folder):
    folder_path = find_folders(ar_name, folder)
    print(folder_path)
    if folder_path:
        cns_files=find_cns_files(folder_path)
        print(cns_files)
        for i in cns_files:
            print(i)
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
            if file.endswith(".cns"):
                cns_files.append(os.path.join(root, file))
    return cns_files


def parse_cns_file(file_path, ar_name):
    try:
        analysis_run = AnalysisRun.objects.get(name=ar_name)
        variants = VariantCall.objects.filter(analysis_run=analysis_run)
        created_objects_count = 0
        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sample_lib = variants.first().sample_lib
                sequencing_run = variants.first().sequencing_run

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
