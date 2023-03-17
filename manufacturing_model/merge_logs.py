"""
merge_logs.py file: MergeLogs class

the class responsibility is to enable the log capabilities for the instantiated model objects, and to save it into a csv
file. Because of the similarity, the logs are also saved into a plain text .txt file and printed on the console.

the second class responsibility is to take all the log output of the simulator and merge it into one unique csv file.
The merged file has to be consistent with time order.

The responsibility is achieved leveraging pandas, turning the log files into dataframes and then merging them performing
a full-outer-join.

"""

import os
import pandas


class MergeLogs(object):
    @staticmethod
    def merge_logs(input_path, output_path, output_name, *args):
        # Initializing the merged_logs.csv file.
        try:
            os.remove(os.path.join(output_path + "/" + output_name))
        except FileNotFoundError:
            print("The log file has not been found in the directory, creating a new one.")
            with open(os.path.join(output_path + "/" + output_name), "w") as f:
                f.close()

        # Creating a list as a buffer to temporally save the data read from the CSVs files.
        df_list = list()
        # Appending the data in the list read from the CSVs files.
        for arg in args:
            df = pandas.read_csv(os.path.join(input_path + "/" + arg))
            df_list.append(df)

        # Merging the first two dataframes.
        df1 = df_list[0]
        df2 = df_list[1]
        df_merge = pandas.merge(left=df1, right=df2, on='step', how="outer", sort=True)

        # Merging the remaining dataframes, if any.
        for element in range(len(df_list)):
            # Skipping the first two dataframes in the list, because they have been merged few lines before.
            if element == 0 or element == 1:
                continue
            # Merging the remaining files.
            else:
                df_merge = pandas.merge(left=df_merge, right=df_list[element], on='step', how='outer', sort=True)

        # Handling missing data generated from machine breakdowns
        df_merge.fillna(method="ffill", inplace=True)
        # Converting all the data into int comprised Trues and Falses
        df_merge.iloc[:, 1:] = df_merge.iloc[:, 1:].astype('Int64')
        # Saving the merged dataframe into a csv file.
        df_merge.to_csv(os.path.join(output_path + '/' + output_name), index=False)


# File Main entry point.
if __name__ == '__main__':
    # Get all the log sub-folders
    folder_list = os.listdir('logs')

    # Considering only sub-folders with the last word as "log"
    target_folder = [x for x in folder_list if x.startswith('.') != True][0]

    # Create a new folder inside it for merged logs
    raw_log_path = os.path.join('logs/' + target_folder)
    merged_log_path = os.path.join('logs/' + target_folder + '/merged_logs')   # Relative path
    os.mkdir(merged_log_path)

    # Get all the Machine_x.csv files in the folder
    folder_list = os.listdir(raw_log_path)

    # Select the keys to iterate
    folder_list = [x for x in folder_list if '.' not in x and 'Machine' in x]

    # Iter in the Machine file list
    log_merger = MergeLogs()
    for component in folder_list:
        # For each group of file, operate a merge over the flags.
        in_path = os.path.join(raw_log_path + '/' + component)
        out_path = merged_log_path
        out_file = component + '.csv'
        merge_file_1 = component.split('_')[0] + ' ' + component.split('_')[1] + ' log.csv'
        merge_file_2 = component.split('_')[0] + ' ' + component.split('_')[1] + ' exp_prod_flag.csv'

        log_merger.merge_logs(in_path, out_path, out_file, merge_file_1, merge_file_2)

    file_list = [x + '.csv' for x in folder_list]

    # Merging into 1.
    log_merger.merge_logs(merged_log_path, merged_log_path, "merged_logs.csv", *file_list)
