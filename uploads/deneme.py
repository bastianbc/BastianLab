import os, sys
from collections import defaultdict

files = os.listdir("files")

# Dosya isimlerini gruplamak için bir sözlük oluştur
file_groups = defaultdict(list)

# Dosya isimlerini grupla
for file_name in files:
    parts = file_name.split('_')[:2]  # İlk iki bölümü al
    group_key = '_'.join(parts)  # Grup anahtarı oluştur
    file_groups[group_key].append(file_name)  # Grup içine dosyayı ekle
print( file_groups.items())
#
# # Sonuçları yazdır
# for group_key, group_files in file_groups.items():
#     print(f"Grup: {group_key}")
#     for file_name in group_files:
#         print(f"  {file_name}")
#     print()
