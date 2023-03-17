"""
global_variables.py file: GlobalVariables class

Class containing the global variables for the model.
"""


class GlobalVariables(object):
    # LOGISTIC PARAMETERS ----------------------------------------------------------------------------------------------

    # NOTE: Containers critical levels
    # Critical stock should be 1 business day greater than supplier take to come

    # 1.Node A Raw Container
    CONTAINER_A_RAW_CAPACITY = 500
    INITIAL_A_RAW = 200
    CRITICAL_STOCK_A_RAW = 50
    SUPPLIER_LEAD_TIME_A_RAW = 0
    SUPPLIER_STD_SUPPLY_A_RAW = 50
    AFTER_REFILLING_CHECK_TIME_A_RAW = 8
    STANDARD_A_CHECK_TIME = 1

    # 2.Node A Finished Container
    CONTAINER_A_FINISHED_CAPACITY = 500
    INITIAL_A_FINISHED = 0
    # Put at one more than the container total capacity to disable.
    CRITICAL_STOCK_A_FINISHED = CONTAINER_A_FINISHED_CAPACITY + 1
    DISPATCHER_LEAD_TIME_A_FINISHED = 0
    DISPATCHER_STD_RETRIEVE_A_FINISHED = 0
    DISPATCHER_RETRIEVED_CHECK_TIME_A_FINISHED = 0
    DISPATCHER_STD_CHECK_TIME_A_FINISHED = 0

    # 3.Node B Raw Container
    CONTAINER_B_RAW_CAPACITY = 500
    INITIAL_B_RAW = 200
    CRITICAL_STOCK_B_RAW = 50
    SUPPLIER_LEAD_TIME_B_RAW = 0
    SUPPLIER_STD_SUPPLY_B_RAW = 50
    AFTER_REFILLING_CHECK_TIME_B_RAW = 8
    STANDARD_B_CHECK_TIME = 1

    # 3.Node B Finished Container
    CONTAINER_B_FINISHED_CAPACITY = 500
    INITIAL_B_FINISHED = 0
    # Put at one more than the container total capacity to disable.
    CRITICAL_STOCK_B_FINISHED = CONTAINER_B_FINISHED_CAPACITY + 1
    DISPATCHER_LEAD_TIME_B_FINISHED = 0
    DISPATCHER_STD_RETRIEVE_B_FINISHED = 0
    DISPATCHER_RETRIEVED_CHECK_TIME_B_FINISHED = 0
    DISPATCHER_STD_CHECK_TIME_B_FINISHED = 0

    # 3.Node C Finished Container
    CONTAINER_C_FINISHED_CAPACITY = 500
    INITIAL_C_FINISHED = 0
    CRITICAL_STOCK_C_FINISHED = 50
    DISPATCHER_LEAD_TIME_C_FINISHED = 0
    DISPATCHER_STD_RETRIEVE_C_FINISHED = 0
    DISPATCHER_RETRIEVED_CHECK_TIME_C_FINISHED = 8
    DISPATCHER_STD_CHECK_TIME_C_FINISHED = 1
    # Total delivered pieces.
    DELIVERED_PIECES = 0

    # Warehouse get and put standard delay
    GET_STD_DELAY = 1
    PUT_STD_DELAY = 1

    # PROCESS PARAMETERS ----------------------------------------------------------------------------------------------
    RANDOM_SEED = 42

    # 1.Node A
    NUM_MACHINES_A = 1              # Number of machines in the work-shop.
    MEAN_PROCESS_TIME_A = 250       # Avg. processing time in seconds - std 3,83 min = 230 sec
    SIGMA_PROCESS_TIME_A = 15       # Sigma processing time in seconds.
    MTTF_A = 77760                  # Mean time to failure in seconds - Standard value: 20 hours = 1200 min = 72000 sec
    MTTR_A = 10800                  # Time to repair a machine in seconds - Standard value: 4 h = 240 min = 14400 sec
    # Standard Availability = 87,8%
    # Standard Un-Availability = 12,2%

    # 2.Node B
    NUM_MACHINES_B = 1              # Number of machines in the work-shop.
    MEAN_PROCESS_TIME_B = 250       # Avg. processing time in seconds - Standard value: 4,0 min = 240 sec
    SIGMA_PROCESS_TIME_B = 15       # Sigma processing time in seconds.
    MTTF_B = 86400                  # Mean time to failure in seconds - Standard value: 24 hours = 14400 min = 86400 sec
    MTTR_B = 12000                  # Time to repair a machine in seconds - Standard value: 3,33 h = 200 min = 12000 sec
    # Standard Availability = 87,8%
    # Standard Un-Availability = 12,2%

    # 3.Node C
    NUM_MACHINES_C = 1              # Number of machines in the work-shop.
    MEAN_PROCESS_TIME_C = 230       # Avg. processing time in seconds - Standard value: 4,17 min = 250 sec
    SIGMA_PROCESS_TIME_C = 10       # Sigma processing time in seconds.
    MTTF_C = 100800                 # Mean time to failure in seconds - Standard value: 28 hours = 1680 min = 100800 sec
    MTTR_C = 9600/5                 # Time to repair a machine in seconds - Standard value: 2,67 h = 160 min = 9600 sec
    # Standard Availability = 91,3%
    # Standard Un-Availability = 8,7%

    # SIM PARAMETERS ---------------------------------------------------------------------------------------------------
    WORKING_SECS = 60               # Working seconds for a minute in a day
    WORKING_MINS = 60               # Working minutes for an hour in a day
    WORKING_HOURS = 8               # Working hours in a day - for test purposes keep 8hours/day
    SHIFTS_IN_A_WORKING_DAY = 1     # Number of shifts in a day - for test purposes keep 1 shift/day
    BUSINESS_DAYS = 1               # Business days in a week - for test purposes keep 5 days/week
    WORKING_WEEKS = 36              # Business weeks in a month - for test purposes keep 12/24/36 weeks

    # Total simulation time in minutes - for test purposes keep 60/90/120 total days
    SIM_TIME = WORKING_SECS * WORKING_MINS * WORKING_HOURS * SHIFTS_IN_A_WORKING_DAY * BUSINESS_DAYS * WORKING_WEEKS

    # LOG PARAMETERS ---------------------------------------------------------------------------------------------------
    LOG_FILENAME = "Log.txt"

    # OTHER PARAMETERS -------------------------------------------------------------------------------------------------

    # CLASS METHODS ----------------------------------------------------------------------------------------------------
