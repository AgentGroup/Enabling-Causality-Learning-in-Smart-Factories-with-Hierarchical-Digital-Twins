"""
transference_system.py file: TransferenceSystem class

Class that has the responsibility to move material from the raw container A and B to the container C.
Written in the most generic way, still a class taylor made to solve a singular problem.
"""


# TRANSFERENCE SYSTEM CLASS --------------------------------------------------------------------------------------------
class TransferenceSystem(object):
    """
    Takes as input one (more in the future) input containers and one output container.
    """
    def __init__(self, env, process_name, input_containers, output_container):
        self.env = env
        self._process_name = process_name
        self._input_containers = input_containers    # This is passed as a list
        self._output_container = output_container

        env.process(self._material_transfer(self.env))

    #  Function describing the machine process.
    def _material_transfer(self, env):

        while True:
            # Assuming that the input buffers are not empty and the output are not full.
            input_empty = False

            # Looping all the input elements...
            for element in range(len(self._input_containers)):
                # ...if the input element is empty, change the flag in True.
                if self._input_containers[element].level == 0:
                    input_empty = True
                    break
                else:
                    input_empty = False

            # ...if the output container is full, change the flag in True.
            if self._output_container.level == self._output_container.capacity:
                output_full = True
            else:
                output_full = False

            # If the input buffers are not full ...
            if (not output_full) & (not input_empty):
                # ... get all the material in the input container ...

                for element in range(len(self._input_containers)):
                    self._input_containers[element].get(1)
                # ... and put the material into the output container
                self._output_container.put(1)

            # Then wait one time-step and re-do the buffer checking.
            yield env.timeout(1)
