import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
from matplotlib import pylab
import base64
from PIL import Image
import os
from io import BytesIO

def generate_graph(ar_name,file_path):
 # CSV verilerini okuma
   print("^"*100, file_path)
   df = pd.read_csv(file_path, on_bad_lines='skip')
   print(df)
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

   