import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
import pandas as pd
from samplelib.models import SampleLib, NA_SL_LINK
from sequencingfile.models import SequencingFile
from sequencingrun.models import SequencingRun
from django.core import serializers
from areas.models import Areas
from libprep.models import NucAcids,AREA_NA_LINK
from blocks.models import Blocks
from capturedlib.models import CapturedLib, SL_CL_LINK
# Specify the directory you want to start from
directory = '/Volumes/labshare/BastianRaid-02/HiSeqData/Acral_Mel_Exome-01/bastianb-AGEX-01/@@md5checksum.txt'
# Replace with your directory path
columns = ["Sequencing Run", "Sequencing Library", "Captured Library", "Sample Library", "File", "Nucleic Acid", "Area", "Block", "Patient"]
df = pd.DataFrame(columns=columns)
# Lists for storing the names of files and directories
df2 = pd.read_csv(directory, index_col=False, encoding='iso-8859-1', on_bad_lines='warn')

def merge_dicts(series):
    merged_dict = {}
    for d in series:
        merged_dict.update(d)
    return merged_dict

def read_rows(row):
    try:
        checksum, file = row.values[0].split()
        print(file)
        sl = file.split("_S")[0]
        d = {
            "Sequencing Run":"Acral_Mel_Exome-01",
            "Sequencing Library":None,
            "Captured Library":None,
            "Sample Library": sl,
            "File": None,
            "Nucleic Acid":None,
            "Area":None,
            "Block":None,
            "Patient":None
        }
        sequencing_run, _ = SequencingRun.objects.get_or_create(name="Acral_Mel_Exome-01")
        seq_file = SequencingFile.objects.get(name=file)
        sample_lib = SampleLib.objects.get(name=sl)
        captured_libs = SL_CL_LINK.objects.filter(sample_lib=sample_lib)
        d["Captured Library"] = [cl.name for cl in captured_libs]
        na = NA_SL_LINK.objects.filter(sample_lib=sample_lib)
        d["Nucleic Acid"] = [na_link.nucacid.name for na_link in na]
        areas = AREA_NA_LINK.objects.filter(nucacid__in=[na_link.nucacid for na_link in na])
        d["Area"] = [area.area.name for area in areas]
        d["Block"] = [area.area.block.name for area in areas]
        d["Patient"] = [area.area.block.patient.pat_id for area in areas]
        d["File"] = {file:checksum}
        df.loc[len(df)] = d
        # pd.concat([df, df_dictionary], ignore_index=True)

    except Exception as e:
        if not "fastq" in row.values[0]:
            return
        checksum, file = row.values[0].split()
        sl = file.split("_S")[0]
        d = {
            "Sequencing Run": "Acral_Mel_Exome-01",
            "Sequencing Library": None,
            "Captured Library": None,
            "Sample Library": sl,
            "File": {file: checksum},
            "Nucleic Acid": None,
            "Area": None,
            "Block": None,
            "Patient": None
        }
        df.loc[len(df)] = d
        print(e)


def create_file():
    df2.apply(lambda row: read_rows(row), axis=1)
    # print(df)
    # grouped_df = df.groupby('Sample Library')['File'].agg(merge_dicts).reset_index()
    df.to_csv("Acral_Mel_Exome-01.csv", index=False)


# if __name__ == "__main__":
#     create_file()