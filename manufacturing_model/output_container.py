"""
output_container.py file: OutputContainer class

This class extends the Container/Store Class of SimPy, integrating the level control.
The level control is needed in order to not run out of available space.

Is possible to exclude the level control service.
"""

import simpy
from txt_logger import TxtLogger
from global_variables import GlobalVariables


class OutputContainer(simpy.Container):
    def __init__(self, env, name, log_path, max_capacity, init_capacity, output_control=True,
                 critical_level_output_container=50, dispatcher_lead_time=0, dispatcher_retrieved_check_time=8,
                 dispatcher_std_check_time=1):
        super().__init__(env, max_capacity, init_capacity)
        self.env = env
        self.name = name

        # The following container has to be always full. The stock-out is to avoid.
        self.env.process(self._output_control_container())

        # Basic parameters
        self._output_control = output_control
        self._critical_level_output_container = critical_level_output_container
        self._dispatcher = dispatcher_lead_time
        self._dispatcher_lead_time = dispatcher_lead_time
        self._dispatcher_retrieved_check_time = dispatcher_retrieved_check_time
        self._dispatcher_std_check_time = dispatcher_std_check_time

        self.products_stored = 0
        self.products_delivered = 0

        # Logging objects
        # No local log path is used because the log is only global for logistics instances
        self.global_txt_logger = TxtLogger(log_path, GlobalVariables.LOG_FILENAME)
        # The following line is not printed ... Why? maybe delete it.
        self.global_txt_logger.write_txt_log_file('### DATA LOG FROM OUTPUT CONTAINER FILE ###\n')

    def _output_control_container(self):
        yield self.env.timeout(0)

        # If the output container service has been activated in the object instantiation...
        while self._output_control:

            # Check container level. If under the critical level, start the emptying process.
            if self.level >= self._critical_level_output_container:

                # Logging the event.
                text = '{0}.1 - out_log: container {1} dispatch stock upper the critical level{2}, {3} pieces left.\n' \
                       'Calling the dispatcher\n'

                print(text.format(self.env.now, self.name, self._critical_level_output_container, self.level))
                print('----------------------------------')
                # Writing into the log file - logistic
                self.global_txt_logger.write_txt_log_file(text.format(self.env.now, self.name,
                                                                      self._critical_level_output_container,
                                                                      self.level))

                # Wait for the dispatcher lead time.
                yield self.env.timeout(self._dispatcher_lead_time)

                # Dispatcher arrived, writing in the console.
                text = '{0}.2-out_log: component dispatcher {1} arrived'
                print(text.format(self.env.now, self.name))
                self.global_txt_logger.write_txt_log_file(text.format(self.env.now, self.name))

                # The warehouse will be completely emptied. Counting the material amount.
                self.products_delivered += self.level

                # Logging the event.
                text = '{0}.3-out_log: dispatcher arrived. {1} pieces took by the dispatcher.\n'
                print(text.format(str(self.env.now), str(self.level)))
                print('----------------------------------')
                self.global_txt_logger.write_txt_log_file(text.format(str(self.env.now), str(self.level)))

                # Dispatcher get made after the log; otherwise the level logged would be zero.

                yield self.get(self.level)

                # After the dispatch, check the level status after a given time (usually 8).
                yield self.env.timeout(self._dispatcher_retrieved_check_time)
            else:
                # If no dispatch, check the level status after at the next step.
                yield self.env.timeout(self._dispatcher_std_check_time)
