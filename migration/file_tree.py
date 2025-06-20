import os
from django.conf import settings

def create_file_tree():
    print("start")
    root_dir_list = ['/mnt/sequencingdata']
    file_tree_output_file = 'file_tree_06_20_sequencingdata.txt'
    file_tree_output_file = os.path.join(settings.MEDIA_ROOT, 'file_tree_06_20_sequencingdata.txt')

    with open(file_tree_output_file, 'w') as f:
        for root_dir in root_dir_list:
            for root, dirs, files in os.walk(root_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    f.write(full_path + "\n")
    print("finish")