import datetime
import csv
from io import StringIO
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from pylab import *
from io import BytesIO
from PIL import Image
from matplotlib.backends.backend_agg import FigureCanvasAgg
matplotlib.use('Agg')
from matplotlib import pylab
import base64
from io import TextIOWrapper

class CreateCSV():
    def __init__(self, sample_libs):
        self.sample_libs = []

    def initial_content(self):
        cols = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
        constant_data = ["STD 1", "STD 2", "STD 3", "STD 4", "STD 5", "STD 6", "NTC", "EMPTY"]
        # listB = []
        for i in range(1, 37):
            self.sample_libs.append("Sample Library " + str(i))

        # Let's create groups of 8
        grouped_sample_libs = [self.sample_libs[j:j + 8] for j in range(0, len(self.sample_libs), 8)]

        # Let's duplicate grouped selected items without last one
        extended_sample_libs = []
        for group in grouped_sample_libs[:-1]:
            duplicated_sub_array = group.copy()
            extended_sample_libs.extend([duplicated_sub_array, duplicated_sub_array])

        # Duplicate the last group elements and make them consecutive pairs
        last_group = grouped_sample_libs[-1]
        tmp = [item for item in last_group for _ in range(2)]
        extended_sample_libs.append(tmp)

        # Add the ConstantData array to the beginning of extendSelectedItems three times
        for _ in range(3):
            extended_sample_libs.insert(0, constant_data.copy())

        # create a matrix from cols and rows
        matrix = [[row + str(col) for col in cols] for row in rows]

        # Pair the matrix and data
        merged_array = []
        for i in range(len(matrix)):
            array_a = matrix[i]
            merged_sub_array = []
            for j in range(len(extended_sample_libs)):
                merged_sub_array.append([array_a[j], extended_sample_libs[j][i]])
            merged_array.append(merged_sub_array)

        return merged_array

    def generate_file_name(self):
        # Get the current date and format it as MMDDYY
        today = datetime.datetime.today()
        date_string = today.strftime('%m%d%y')

        # Extract SL prefixes
        prefixes = set()
        for sl_name in self.sample_libs:
            prefix = sl_name.split('-')[0]  # Get the prefix before the dash
            prefixes.add(prefix)

        # Combine prefixes
        prefix_string = '+'.join(sorted(prefixes))

        # Combine date and prefixes
        file_name = f"{date_string}-{prefix_string}.csv"
        return file_name

    def generate_csv(self,content):
        # Create a StringIO object to hold the CSV data
        csv_data = StringIO()
        print(content)
        # Write the CSV data to the StringIO object
        writer = csv.writer(csv_data)
        for row in content:
            writer.writerow([item[0] for item in row])  # Write only the data part to CSV

        return csv_data.getvalue()

    def get_value(self):
        content = self.initial_content()
        return self.generate_csv(content)

class QPCRAnalysis():
    def __init__(self, file):
        self.file = file
        self.standart_data = []
        self.samples = []
        self.intercept = None
        self.slope = None
        self._extract_data()

    def _extract_data(self):
        # Wrap the file in a TextIOWrapper to decode it from bytes to string
        file_wrapper = TextIOWrapper(self.file, encoding='utf-8')

        # Now use the wrapped file to create a CSV reader
        reader = csv.reader(file_wrapper)

        row = next(reader)  # Skip the first row (assuming it's a header row)

        # Raw qPCR data: STD number from column name, concentration in pM from column status, Ct values from column Cp in cp.text
        values = []
        tmp = []
        for i,row in enumerate(reader):
            index = i % 12
            if index<3:
                if row[3].startswith("STD"):
                    std_number = float(row[3][-1])
                    concentration_pm = float(row[6])
                    ct_value = 0 if row[4] == "" else float(row[4])
                    self.standart_data.append([std_number, concentration_pm, ct_value])
            elif index>=3 and index<=10:
                ct_value = 0 if row[4] == "" else float(row[4])
                sample_lib = row[3]
                values.append((sample_lib,ct_value))
            else:
                print(row)
                ct_value = 0 if row[4] == "" else float(row[4])
                sample_lib = row[3]
                tmp.append((sample_lib,ct_value))
        values.extend(tmp)
        # Sample data: # Sample data of three SLs with their duplicates in positions 1 and 2 of the tuple and a constant Average fragment length (bp) of 999 to be added for all in position 3 of the tuple]
        self.samples = [[values[i][1], values[i + 1][1], 999, values[i][0]] for i in range(0, len(values), 2)]

    def create_normalization_curve(self):
        raw_data = np.array(self.standart_data)
        # Calculate the average Ct value for each concentration
        unique_concentrations = np.unique(raw_data[:,1])
        avg_Ct_values = np.array([np.mean(raw_data[raw_data[:,1] == concentration, 2]) for concentration in unique_concentrations])

        # Log transform the concentrations for linear regression
        log_concentrations = np.log10(unique_concentrations)

        # Perform linear regression
        self.slope, self.intercept, r_value, p_value, std_err = linregress(log_concentrations, avg_Ct_values)

        # Calculate R-squared value
        r_squared = r_value**2

        # Generate points for the regression line
        regression_line = self.slope * log_concentrations + self.intercept

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(log_concentrations, avg_Ct_values, 'o', label='Average data', markersize=10)
        plt.plot(log_concentrations, regression_line, 'r', label=f'Fitted line: slope={self.slope:.2f}, intercept={self.intercept:.2f}\nR-squared={r_squared:.2f}')
        plt.title('qPCR Standard Curve')
        plt.xlabel('Log(Concentration)')
        plt.ylabel('Average Ct Values')
        plt.legend()
        plt.grid(True)

        buffer = BytesIO()
        canvas = pylab.get_current_fig_manager().canvas
        canvas.draw()
        pilImage = Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
        pilImage.save(buffer, "PNG")

        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def calculate_concentration(self):
        # Standard fragment length in bp
        standard_fragment_length = 452
        # Dilution factor
        dilution_factor = 25000

        results = []
        for sample in self.samples:
            average_cq = np.mean(sample[:2])
            log_concentration = (average_cq - self.intercept) / self.slope
            concentration_pm = 10**log_concentration  # Convert log to linear scale

            # Adjust concentration based on fragment length
            size_adjusted_concentration_pm = concentration_pm * (standard_fragment_length / sample[2])
            undiluted_concentration_pm = size_adjusted_concentration_pm* dilution_factor
            # Convert pM to nM for undiluted library
            undiluted_library_nm = undiluted_concentration_pm / 1000
            # Calculate concentration in ng/µL using the size-adjusted concentration
            concentration_undiluted_library_ng_ul = (size_adjusted_concentration_pm * dilution_factor / 1000) * (sample[2] * 617.9 / 1e6)
            results.append((sample[3],concentration_undiluted_library_ng_ul))

        return results
