"""
csv_logger.py file: CsvLogger class

the class responsibility is to enable the log capabilities for the instantiated model objects and to save them as a .csv
file.
"""

import os


class CsvLogger(object):
    def __init__(self, csv_log_path, csv_log_filename):
        self._csv_log_path = csv_log_path
        self._csv_log_filename = csv_log_filename

        self._complete_csv_filename = os.path.join(self._csv_log_path + "/" + self._csv_log_filename)

        self._heading = self._csv_log_filename.split("log.")[0].strip()

    def initialise_csv_log_file(self, head):
        try:
            with open(self._complete_csv_filename, "w") as f:
                f.close()
        except FileExistsError:
            print('The log file already exists, cleaning up and creating a new one.')
            os.remove(self._complete_csv_filename)
            with open(self._complete_csv_filename, "w") as f:
                f.close()

        with open(self._complete_csv_filename, "a") as f:
            f.write(head)
            f.close()

    def write_csv_log_file(self, data_list):
        # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR, expectation_not_met
        text = ''

        # For each line in the data_list ...
        for i in range(len(data_list)):
            # Adding comma between data, avoiding comma at the end of the line
            # ... for each element in the data_list ...
            for j in range(len(data_list[i])):
                # ... if the element is the last in the line ...
                if j + 1 == len(data_list[i]):
                    # ... add the string to the text and a newline character.
                    text = text + str(data_list[i][j]) + "\n"
                else:
                    # ... else, just add the string to the text.
                    text = text + str(data_list[i][j]) + ","

        with open(self._complete_csv_filename, "a") as f:
            f.write(text)
            f.close()
