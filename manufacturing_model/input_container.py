"""
input_container.py file: InputContainer class

This class extends the Container/Store Class of SimPy, integrating the level control.
The level control is needed in order to have always some material available.

Is possible to exclude the level control service.
"""

import simpy
from txt_logger import TxtLogger
from global_variables import GlobalVariables


class InputContainer(simpy.Container):
    def __init__(self, env, name, log_path, max_capacity, init_capacity, input_control=True,
                 critical_level_input_container=50, supplier_lead_time=0, supplier_std_supply=50,
                 input_refilled_check_time=8, input_std_check_time=1):
        super().__init__(env, max_capacity, init_capacity)
        self.name = name
        self._env = env

        # The following container has to be always full. The stock-out is to avoid.
        self._env.process(self._input_control_container())

        # Basic parameters
        self._input_control = input_control
        self._critical_level = critical_level_input_container
        self._supplier_lead_time = supplier_lead_time
        self._supplier_std_supply = supplier_std_supply
        self._after_refilling_check_time = input_refilled_check_time
        self._std_check_time = input_std_check_time

        self.products_picked = 0

        # Logging objects
        # No local log path is used because the log is only global for logistics instances
        self.global_txt_logger = TxtLogger(log_path, GlobalVariables.LOG_FILENAME)
        # The following line is not printed ... Why? maybe delete it.
        self.global_txt_logger.write_txt_log_file('### DATA LOG FROM INPUT CONTAINER FILE ###\n')

    def _input_control_container(self):
        yield self._env.timeout(0)

        # If the input container service has been activated in the object instantiation...
        while self._input_control:

            # Check container level. If under the critical level, start the emptying process.
            if self.level <= self._critical_level:

                # Logging the event.
                text = '{0}.1 - in_log: container {1} stock under the critical level {2}, {3} pieces left.\n ' \
                       'Calling the component supplier'
                print(text.format(self._env.now, self.name, self._critical_level, self.level))
                print('----------------------------------')
                # Writing into the log file - logistic
                self.global_txt_logger.write_txt_log_file(text.format(self._env.now, self.name, self._critical_level,
                                                                      self.level))

                # Wait for the supplier lead time.
                yield self._env.timeout(self._supplier_lead_time)

                # Supplier arrived, logging the event.
                text = '{0}.2 - in_log: component supplier {1} arrived\n'
                print(text.format(self._env.now, self.name))
                # Writing into the log file - logistic
                self.global_txt_logger.write_txt_log_file(text.format(self._env.now, self.name))

                # The warehouse will be refilled with a standard quantity.
                yield self.put(50)

                # Logging the event.
                text = '{0}.3 - in_log: container {1} new A component stock is {2}\n'
                print(text.format(self._env.now, self.name, self.level))
                print('----------------------------------')
                # Writing into the log file - logistic
                self.global_txt_logger.write_txt_log_file(text.format(self._env.now, self.name, self.level))

                # After the refill, check the level status after a given time (usually 8).
                yield self._env.timeout(self._after_refilling_check_time)
            else:
                # If no dispatch, check the level status after at the next step.
                yield self._env.timeout(self._std_check_time)
