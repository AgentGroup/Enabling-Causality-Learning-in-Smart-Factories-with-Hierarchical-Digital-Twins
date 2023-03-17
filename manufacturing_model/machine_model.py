"""
machine_model.py file: Machine class

Class describing a single machine behaviour.
Random breakdowns are embedded in the model.
Breakdown handling is also implemented during the input-output material handling.

The file have to be integrated with the env.

It takes as input an InputContainer and an OutputContainer object, to get and put raw materials from and in the
warehouses.

The log CSV files are encoded in the time steps in order to make every log unique within each time-step. So, time steps
are defined as "time_step.progressive_number". This was necessary in order to compute a join when merging the produced
log dataframes from the relative CSVs.

The log encoding is the following:

    # Starting cycle log --------------------------------------------
    x.0: a new cycle started, printing the initial state
    # Input buffer logs ---------------------------------------------
    x.1: input buffer empty, waiting one time step till is filled up
    x.2: input buffer filled up, continuing the process
    x.3: breakdown during input material handling
    x.4: repairing during input material handling
    x.5: finished the input material handling
    # Process logs --------------------------------------------------
    x.6: start to work on the part, required time to finish saved
    x.7: breakdown during the part processing
    x.8: repairing during the part processing
    x.9: finish to work on the part, required time to finish at zero
    # Output buffer logs -------------------------------------------
    x.10: output buffer full, waiting one time step till is emptied
    x.11: output buffer emptied, continuing with the process
    x.12: breakdown during output material handling
    x.13: repairing during output material handling
    x.14: finished the output material handling
"""

import os
import random
import simpy
from global_variables import GlobalVariables
from statistics import mean
from csv_logger import CsvLogger
from txt_logger import TxtLogger


# MACHINE CLASS --------------------------------------------------------------------------------------------------------
# noinspection PyPep8Naming
class Machine(object):
    """
    A machine produces parts and occasionally gets broken.

    If it breaks, it requires a "repairman" and continues
    the production when is repaired. - DEACTIVATED IN MY IMPLEMENTATION.

    A machine has a "name" and a number of parts processed.
    """
    def __init__(self, env, name, log_path, mean_process_time, sigma_process_time, MTTF, MTTR, input_buffer,
                 output_buffer):
        self.env = env
        self._name = name                       # Must be coded as "Machine" + identifying letter from A to Z

        # Process variables.
        self.parts_made = 0                     # No private
        self._mean_process_time = mean_process_time
        self._sigma_process_time = sigma_process_time

        # Breakdowns variables.
        self._MTTF = MTTF
        self._break_mean = 1 / self._MTTF
        self._MTTR = MTTR
        self._repair_mean = 1 / self._MTTR
        self._broken = False
        self._breakdown_num_counter = 0
        self._breakdown_time_counter = 0

        self._last_piece_step = 0

        self._input_buffer = input_buffer
        self._output_buffer = output_buffer

        # Simpy processes
        self._process = self.env.process(self._working())
        self.env.process(self._break_machine())

        self._expected_products_sensor = False
        self.env.process(self._expected_products())

        self._logistic_breakdowns = True         # To exclude breakdowns during logistic operations, set to False.
        self._processing_breakdowns = True       # To exclude breakdowns during processing operations, set to False.

        # Logging objects - As a best practice, write before in the txt, console, then append data into the data list.

        # Logging objects
        # Creating the folder that contains the i-th machine log
        os.mkdir(log_path + os.path.join('/Machine_') + self._name.split(" ")[1])
        # Creating the local log path that will be used with log_path that represents the global log path.
        local_log_path = log_path + os.path.join('/Machine_') + self._name.split(" ")[1]
        # Creating logging objects
        self.global_txt_logger = TxtLogger(log_path, GlobalVariables.LOG_FILENAME)
        self.local_txt_logger = TxtLogger(local_log_path, self._name + " log.txt")
        self.csv_logger = CsvLogger(local_log_path, self._name + " log.csv")
        self.expected_products_logger = CsvLogger(local_log_path, self._name + " exp_prod_flag.csv")

        # List containing the csv log files of each machine.
        self._data_list = list()
        # List containing the csv log files of the expected product flag of each machine.
        self._exp_pieces = list()

    # Function describing the machine process.
    def _working(self):
        """
        Produces parts as long as the simulation runs.

        While making a part, the machine may break multiple times.
        When machine breaks, MTTR is computed from its statistics.
        """

        csv_head = 'step,input ' + self._name + ',time process ' + self._name + ',output ' + self._name + \
                   ',produced ' + self._name + ',failure ' + self._name + ',MTTF ' + self._name + \
                   ',repair time ' + self._name + '\n'

        self.csv_logger.initialise_csv_log_file(csv_head)

        # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR, expectation_not_met
        while True:
            # LOG THE INITIAL STATE OF THE STEP ----------------------------------------------------------------------
            self._write_extended_log(self.env.now, '0', self._input_buffer.level, '0', self._output_buffer.level,
                                     self.parts_made, self._broken, self._MTTF, '0')

            # CHECK THE INPUT BUFFER LEVEL -----------------------------------------------------------------------------
            # Perform the output warehouse level checking: if empty, wait 1 time step.
            # If in the input buffer there is no raw material ...
            if self._input_buffer.level == 0:
                # ... and while the buffer is empty ...
                while self._input_buffer.level == 0:
                    # ... log the status ...
                    # Maybe this log is not necessary due to the initial state log... think about it
                    self._write_extended_log(self.env.now, '1', self._input_buffer.level, '0',
                                             self._output_buffer.level, self.parts_made, self._broken, self._MTTF, '0')
                    try:
                        # ... and wait one time step.
                        yield self.env.timeout(1)
                    except simpy.Interrupt:
                        pass
                # When the buffer is filled, log the status and continue.
                self._write_extended_log(self.env.now, '2', self._input_buffer.level, '0',
                                         self._output_buffer.level, self.parts_made, self._broken, self._MTTF, '0')

            # HANDLING INPUT MATERIAL ----------------------------------------------------------------------------------
            # Take the raw product from raw products warehouse. Wait the necessary step to retrieve the material.
            # The action is performed in a try-except block because the machine may break during the handling of the
            # material
            handled_in = GlobalVariables.GET_STD_DELAY
            start_handling = 0
            while handled_in:
                try:
                    # Handling the part
                    start_handling = self.env.now
                    # No handling logging - Maybe it should be added?
                    yield self.env.timeout(handled_in)
                    # handled_in set 0 to exit to the loop
                    handled_in = 0

                except simpy.Interrupt:
                    # If machine breakdowns are considered during logistic operations into the simulation...
                    if self._logistic_breakdowns:
                        # ... then simulate the process stop for the machine breakdown and relative time to repair

                        # The machine broke.
                        self._broken = True
                        handled_in -= self.env.now - start_handling  # How much time left to handle the material?

                        break_down_time = int(random.expovariate(self._repair_mean))

                        self._write_extended_log(self.env.now, '3', self._input_buffer.level, '0',
                                                 self._output_buffer.level, self.parts_made, self._broken, '0',
                                                 break_down_time)

                        # The yield value is truncate in order to have int time-steps
                        yield self.env.timeout(break_down_time)

                        # Count breakdown number and time.
                        self._breakdown_num_counter += 1
                        self._breakdown_time_counter += break_down_time

                        # Machine repaired.
                        self._broken = False

                        self._write_extended_log(self.env.now, '4', self._input_buffer.level, '0',
                                                 self._output_buffer.level, self.parts_made, self._broken, self._MTTF,
                                                 '0')
                    else:
                        # ... else, skip the time to repair wait and go ahead.
                        pass

            # Logging the event.
            self._input_buffer.get(1)  # Take the piece from the input buffer
            self._input_buffer.products_picked += 1  # Track the total products picked from the buffer

            self._write_extended_log(self.env.now, '5', self._input_buffer.level, '0', self._output_buffer.level,
                                     self.parts_made, self._broken, self._MTTF, '0')

            # PROCESSING THE MATERIAL ----------------------------------------------------------------------------------
            # Start making a new part
            time_per_part = int(random.normalvariate(self._mean_process_time, self._sigma_process_time))
            # time_per_part = self._mean_process_time
            done_in = time_per_part
            start = 0
            while done_in:
                try:
                    # Working on the part
                    start = self.env.now

                    self._write_extended_log(self.env.now, '6', self._input_buffer.level, done_in,
                                             self._output_buffer.level, self.parts_made, self._broken, self._MTTF, '0')
                    # The yield value is truncate in order to have int time-steps
                    yield self.env.timeout(done_in)
                    # Set 0 to exit to the loop
                    done_in = 0

                except simpy.Interrupt:
                    # If machine breakdowns are considered during machine operations into the simulation...
                    if self._processing_breakdowns:
                        # ... then simulate the process stop for the machine breakdown and relative time to repair
                        # wait...

                        # The machine broke.
                        self._broken = True
                        done_in -= self.env.now - start     # How much time left to finish the job?

                        # Count breakdown number and time.
                        break_down_time = int(random.expovariate(self._repair_mean))

                        self._write_extended_log(self.env.now, '7', self._input_buffer.level, done_in,
                                                 self._output_buffer.level, self.parts_made, self._broken, '0',
                                                 break_down_time)

                        # The yield value is truncate in order to have int time-steps
                        yield self.env.timeout(break_down_time)

                        # Count breakdown number and time.
                        self._breakdown_num_counter += 1
                        self._breakdown_time_counter += break_down_time

                        # Machine repaired.
                        self._broken = False

                        self._write_extended_log(self.env.now, '8', self._input_buffer.level, done_in,
                                                 self._output_buffer.level, self.parts_made, self._broken, self._MTTF,
                                                 '0')
                    else:
                        # ... else, skip the time to repair wait and go ahead.
                        pass

            # Part is done
            prod_time = self.env.now
            self._last_piece_step = prod_time
            self.parts_made += 1

            self._write_extended_log(prod_time, '9', self._input_buffer.level, '0', self._output_buffer.level,
                                     self.parts_made, self._broken, self._MTTF, '0')

            # CHECK THE OUTPUT BUFFER LEVEL ----------------------------------------------------------------------------
            # Perform the output warehouse level checking: if full, wait 1 time step.
            # If the output buffer is full ...
            if self._output_buffer.level == self._output_buffer.capacity:
                # ... and while the buffer is still full ...
                while self._output_buffer.level == self._output_buffer.capacity:
                    # ... log the status ...
                    self._write_extended_log(self.env.now, '10', self._input_buffer.level, '0',
                                             self._output_buffer.level, self.parts_made, self._broken, self._MTTF, '0')

                    try:
                        # ... and wait one time step.
                        yield self.env.timeout(1)
                    except simpy.Interrupt:
                        pass
                # When the buffer is emptied, log the status and continue.
                self._write_extended_log(self.env.now, '11', self._input_buffer.level, '0',
                                         self._output_buffer.level, self.parts_made, self._broken, self._MTTF, '0')

            # HANDLING OUTPUT MATERIAL ---------------------------------------------------------------------------------
            handled_out = GlobalVariables.PUT_STD_DELAY
            start_handling = 0
            while handled_out:
                try:
                    # Handling the part
                    start_handling = self.env.now
                    # No handling logging - Maybe it should be added?
                    yield self.env.timeout(handled_out)
                    handled_out = 0  # Set 0 to exit to the loop

                except simpy.Interrupt:
                    # If machine breakdowns are considered during logistic operations into the simulation...
                    if self._logistic_breakdowns:
                        # ... then simulate the process stop for the machine breakdown and relative time to repair

                        # The machine broke.
                        self._broken = True
                        handled_out -= self.env.now - start_handling  # How much time left to handle the material?

                        # Count breakdown number and time.
                        break_down_time = int(random.expovariate(self._repair_mean))

                        self._write_extended_log(self.env.now, '12', self._input_buffer.level, '0',
                                                 self._output_buffer.level, self.parts_made, self._broken, '0',
                                                 break_down_time)

                        # The yield value is truncate in order to have int time-steps
                        yield self.env.timeout(break_down_time)

                        # Count breakdown number and time.
                        self._breakdown_num_counter += 1
                        self._breakdown_time_counter += break_down_time

                        # Machine repaired.
                        self._broken = False

                        self._write_extended_log(self.env.now, '13', self._input_buffer.level, '0',
                                                 self._output_buffer.level, self.parts_made, self._broken, self._MTTF,
                                                 '0')
                    else:
                        # ... else, skip the time to repair wait and go ahead.
                        pass

            # Handling_out is done
            # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._output_buffer.put(1)                # Take the piece from the input buffer
            self._output_buffer.products_stored += 1  # Track the total products stored in the buffer

            self._write_extended_log(self.env.now, '14', self._input_buffer.level, '0', self._output_buffer.level,
                                     self.parts_made, self._broken, self._MTTF, '0')

            # The single product making is end!

            # Writing all the collected file into the csv.
            self.csv_logger.write_csv_log_file(self._data_list)
            # Resetting the data collecting list.
            self._data_list = list()
            # Going at the next time-step
            try:
                yield self.env.timeout(1)
            except simpy.Interrupt:
                pass

    def _break_machine(self):
        """Occasionally break the machine."""
        random.seed(0)
        while True:
            # Extract the next failure step following the MTTF distribution
            time_to_failure = int(random.expovariate(self._break_mean))
            # Block the failure triggering process for the TTF extracted time.
            yield self.env.timeout(time_to_failure)
            # If the machine is not already broken and is currently working...
            if not self._broken:
                self._process.interrupt()

    def _expected_products(self):
        check_error_tolerance = mean([GlobalVariables.MEAN_PROCESS_TIME_A, GlobalVariables.MEAN_PROCESS_TIME_B,
                                      GlobalVariables.MEAN_PROCESS_TIME_C])

        csv_head = 'step,' + self._name + ' flag\n'
        self.expected_products_logger.initialise_csv_log_file(csv_head)

        while True:
            try:
                if (self._last_piece_step + self._mean_process_time + int(check_error_tolerance)) < self.env.now:
                    self._expected_products_sensor = True
                    self._exp_pieces.append([self.env.now, self._expected_products_sensor])
                else:
                    self._expected_products_sensor = False
                    self._exp_pieces.append([self.env.now, self._expected_products_sensor])
            except simpy.Interrupt:
                pass

            self.expected_products_logger.write_csv_log_file(self._exp_pieces)
            self._exp_pieces = list()

            yield self.env.timeout(1)

    def _write_extended_log(self, step, moment, input_level, done_in, output_level, parts_made, broken, MTTF, TTR):
        # Signature = step, moment, input_level, done_in (time_process), output_level, parts_made (produced), broken,
        # MTTF, MTTR
        if moment == "0":
            text = "{0}.{1} - mach: state of {2} at step {0} moment {1}: input buffer {3}, output buffer {4}\n"
            # Print in the console
            print(text.format(step, moment, self._name, input_level, output_level))
            # Print in the txt file
            self.global_txt_logger.write_txt_log_file(text.format(step, moment, self._name, input_level, output_level))
            self.local_txt_logger.write_txt_log_file(text.format(step, moment, self._name, input_level, output_level))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._data_list.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made,
                                    broken, MTTF, TTR])

        if moment == "1":
            text = "{0}.{1} - mach: the {2} input buffer level is {3}. Waiting 1 time step and re-check.\n"
            # Print in the console
            print(text.format(step, moment, self._name, input_level))
            # Print in the txt file
            self.global_txt_logger.write_txt_log_file(text.format(step, moment, self._name, input_level))
            self.local_txt_logger.write_txt_log_file(text.format(step, moment, self._name, input_level))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._data_list.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made,
                                    broken, MTTF, TTR])

        if moment == "2":
            text = "{0}.{1} - mach: the {2} input buffer has been filled up. The buffer level is {3}. Continuing with "\
                   "the process\n"
            # Print in the console
            print(text.format(step, moment, self._name, input_level))
            # Print in the txt file
            self.global_txt_logger.write_txt_log_file(text.format(step, moment, self._name, input_level))
            self.local_txt_logger.write_txt_log_file(text.format(step, moment, self._name, input_level))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._data_list.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made,
                                    broken, MTTF, TTR])

        elif moment == "3":
            text = "\n{0}.{1} down - mach: {2} broke. Handling-in stopped. Machine will be repaired in {3}\n"
            # Print in the console
            print(text.format(step, moment, self._name, TTR))
            # Print in the txt file
            self.global_txt_logger.write_txt_log_file(text.format(step, moment, self._name, TTR))
            self.local_txt_logger.write_txt_log_file(text.format(step, moment, self._name, TTR))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._data_list.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made,
                                    broken, MTTF, TTR])

        elif moment == "4":
            text = "\n{0}.{1} up - mach: {2} repaired. Handling-in restarted.\n"
            # Print in the console
            print(text.format(step, moment, self._name))
            # Print in the txt file
            self.global_txt_logger.write_txt_log_file(text.format(step, moment, self._name))
            self.local_txt_logger.write_txt_log_file(text.format(step, moment, self._name))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._data_list.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made,
                                    broken, MTTF, TTR])

        elif moment == "5":
            text = "{0}.{1} - mach: input {2} level {3}; taken 1 from input {2}.\n"
            # Print in the console
            print(text.format(step, moment, self._name, input_level))
            # Print in the txt file
            self.global_txt_logger.write_txt_log_file(text.format(step, moment, self._name, input_level))
            self.local_txt_logger.write_txt_log_file(text.format(step, moment, self._name, input_level))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._data_list.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made,
                                    broken, MTTF, TTR])

        elif moment == "6":
            text = "{0}.{1} - mach: started 1 in {2}. Processing time: {3}\n"
            # Print in the console
            print(text.format(step, moment, self._name, done_in))
            # Print in the txt file
            self.global_txt_logger.write_txt_log_file(text.format(step, moment, self._name, done_in))
            self.local_txt_logger.write_txt_log_file(text.format(step, moment, self._name, done_in))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._data_list.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made,
                                    broken, MTTF, TTR])

        elif moment == "7":
            text = "\n{0}.{1} down - mach: {2} broke. {3} step for the job to be completed. Machine will be repaired " \
                   "in {4}\n"
            # Print in the console
            print(text.format(step, moment, self._name, done_in, TTR))
            # Print in the txt file
            self.global_txt_logger.write_txt_log_file(text.format(step, moment, self._name, done_in, TTR))
            self.local_txt_logger.write_txt_log_file(text.format(step, moment, self._name, done_in, TTR))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._data_list.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made,
                                    broken, MTTF, TTR])

        elif moment == "8":
            text = "\n{0}.{1} up - mach: {2} repaired. Working restarted.\n"
            # Print in the console
            print(text.format(step, moment, self._name))
            # Print in the txt file
            self.global_txt_logger.write_txt_log_file(text.format(step, moment, self._name))
            self.local_txt_logger.write_txt_log_file(text.format(step, moment, self._name))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._data_list.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made,
                                    broken, MTTF, TTR])

        elif moment == "9":
            text = "{0}.{1} - mach: made 1 in {2}. Total pieces made: {3}.\n"
            # Print in the console
            print(text.format(step, moment, self._name, parts_made))
            # Print in the txt file
            self.global_txt_logger.write_txt_log_file(text.format(step, moment, self._name, parts_made))
            self.local_txt_logger.write_txt_log_file(text.format(step, moment, self._name, parts_made))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._data_list.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made,
                                    broken, MTTF, TTR])

        # if statement ready-to-use but case never called in the working method.
        elif moment == "10":
            text = "{0}.{1} - out_full - mach: the {2} output buffer level is {3}. Waiting 1 time step and re-check.\n"
            # Print in the console
            print(text.format(step, moment, self._name, output_level))
            # Print in the txt
            self.global_txt_logger.write_txt_log_file(text.format(step, moment, self._name, output_level))
            self.local_txt_logger.write_txt_log_file(text.format(step, moment, self._name, output_level))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._data_list.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made,
                                    broken, MTTF, TTR])

        elif moment == "11":
            text = "{0}.{1} - mach: the {2} output buffer has been emptied. The buffer level is {3}. Continuing with " \
                   "the process\n"
            # Print in the console
            print(text.format(step, moment, self._name, output_level))
            # Print in the txt file
            self.global_txt_logger.write_txt_log_file(text.format(step, moment, self._name, output_level))
            self.local_txt_logger.write_txt_log_file(text.format(step, moment, self._name, output_level))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._data_list.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made,
                                    broken, MTTF, TTR])

        elif moment == "12":
            text = "\n{0}.{1} down - mach: {2} broke. Handling-out stopped. Machine will be repaired in {3}\n"
            # Print in the console
            print(text.format(step, moment, self._name, TTR))
            # Print in the txt file
            self.global_txt_logger.write_txt_log_file(text.format(step, moment, self._name, TTR))
            self.local_txt_logger.write_txt_log_file(text.format(step, moment, self._name, TTR))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._data_list.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made,
                                    broken, MTTF, TTR])

        elif moment == "13":
            text = "\n{0}.{1} up - mach: {2} repaired. Handling-out restarted.\n"
            # Print in the console
            print(text.format(step, moment, self._name))
            # Print in the txt file
            self.global_txt_logger.write_txt_log_file(text.format(step, moment, self._name))
            self.local_txt_logger.write_txt_log_file(text.format(step, moment, self._name))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._data_list.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made,
                                    broken, MTTF, TTR])

        elif moment == "14":
            text = "{0}.{1} - mach: output {2} level {3}; put 1 in output {2}.\n"
            # Print in the console
            print(text.format(step, moment, self._name, output_level))
            # Print in the txt file
            self.global_txt_logger.write_txt_log_file(text.format(step, moment, self._name, output_level))
            self.local_txt_logger.write_txt_log_file(text.format(step, moment, self._name, output_level))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self._data_list.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made,
                                    broken, MTTF, TTR])
