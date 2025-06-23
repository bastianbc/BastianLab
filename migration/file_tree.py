import os
from django.conf import settings
from sequencingfile.models import SMBDirectory

def create_file_tree():
    print("start")
    root_dirs = ['/mnt/sequencingdata']
    for dir in root_dirs:
        for root, dirs, files in os.walk(dir):
            for file in files:
                full_path = os.path.join(root, file)
                obj, created = SMBDirectory.objects.get_or_create(directory=full_path.strip())
    print("finish")


