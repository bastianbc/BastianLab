import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
import pandas as pd
from django.conf import settings
from sequencingfile.models import SMBDirectory
from pathlib import Path
import pandas as pd



def register_smb():
    output_file = Path("/Users/cbagci/Documents/test/venv/file_tree_06_17_labshare.txt")
    output_file = Path("/Users/cbagci/Documents/test/venv/file_tree_06_17_sequencingdata.txt")

    with open(output_file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]  # remove empty lines

    df = pd.DataFrame(lines, columns=["path"])
    df = df[~df["path"].str.endswith(("/"))]
    df = df[~df["path"].str.endswith(("/.DS_Store"))]
    for path in df["path"]:
        obj, created = SMBDirectory.objects.get_or_create(directory=path.strip())


if __name__ == "__main__":
    print("start")
    register_smb()
    print("end")