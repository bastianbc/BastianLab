import os, logging
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
django.setup()
from django.conf import settings
from variant.models import VariantFile

logger = logging.getLogger("file-tree")

SUFFIX_KEYS = [
    "multianno_Filtered.txt",
    "insert_size_metrics.txt",
    ".dup_metrics",
    "Hs_Metrics.txt",
    "dedup_BSQR.cns",
]

def create_file_tree(root_dir_list, file_tree_file):
    """
    Walk each directory in root_dir_list and write only the files
    ending with one of the SUFFIX_KEYS to file_tree_file.
    """
    with open(file_tree_file, 'w') as f:
        for root_dir in root_dir_list:
            for root, dirs, files in os.walk(root_dir):
                dirs[:] = [d for d in dirs if d not in ('log', 'scripts', 'strelka')]
                for fname in files:
                    print(f"{fname}")
                    flags = [suffix for suffix in SUFFIX_KEYS if fname.endswith(suffix)]
                    if not flags:
                        continue  # skip non-matching files
                    rel_dir = root.replace(settings.SMB_DIRECTORY_SEQUENCINGDATA, "").lstrip(os.sep)
                    var_file, _ = VariantFile.objects.get_or_create(name=fname, directory=rel_dir)
                    print(f"{rel_dir} --> {var_file}")
                    f.write(f"{rel_dir}-->{fname}\n")