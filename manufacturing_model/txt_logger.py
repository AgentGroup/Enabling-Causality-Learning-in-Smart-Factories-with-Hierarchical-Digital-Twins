"""
txt_logger.py file: TxtLogger class

the class responsibility is to enable the log capabilities for the instantiated model objects and to save them as a .txt
file.
"""

import os


class TxtLogger(object):
    def __init__(self, txt_log_path, txt_log_filename):
        self.txt_log_path = txt_log_path
        self.txt_log_filename = txt_log_filename
        self.complete_txt_filename = os.path.join(self.txt_log_path + "/" + self.txt_log_filename)

        self._initialise_txt_log_file()

    def _initialise_txt_log_file(self):
        try:
            os.remove(self.complete_txt_filename)
        except FileNotFoundError:
            print("The log file has not been found in the directory, creating a new one.")
            with open(self.complete_txt_filename, "w") as f:
                f.close()

    def write_txt_log_file(self, text):
        with open(self.complete_txt_filename, "a") as f:
            f.write(text)
            f.close()
