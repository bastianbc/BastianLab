import os
from pathlib import Path

def create_file_tree(root_dirs:list, file_tree_file):
    with open(file_tree_file, 'w') as f:
        for root_dir in root_dirs:
            for root, dirs, files in os.walk(root_dir):
                if "BastianLab/venv" in root or "BastianLab/.git" in root:
                    continue
                f.write('root:{} dirs:{} files: {}\n'.format(root, dirs, files))

root_directory = ['/Users/cbagci/Documents/BastianLab']

file_tree_output_file = 'bastianlab_file_tree.txt'

# Call the function to create the file tree
# create_file_tree(root_directory, file_tree_output_file)
create_file_tree(root_directory, file_tree_output_file)