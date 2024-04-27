import datetime
import csv
from io import StringIO

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
