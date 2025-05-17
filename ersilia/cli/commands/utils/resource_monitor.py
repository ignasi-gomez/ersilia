from signal import *
import sys, time
import platform,psutil,os
import time
#We use numpy as should be already imported for another functionalities
import numpy as np

#Any of these means we finished process
TERMINATION_SIGNAL_SET = [SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM]

#To store stats we gather and clean does not accept more params
REPORT_DATA = {}

#Template for report
REPORT_TEMPLATE = """· Hardware configuration: {HARDWARE_CONFIGURATION}
· Model selected for evaluation: {MODEL_SELECTED}
· CPU STATS:
    · Average CPU load: {CPU_LOAD_AVG} %
    · MIN CPU load: {CPU_LOAD_MIN} %
    · MAX CPU load: {CPU_LOAD_MAX} %
· Memory STATS:
    · Average memory ussage: {MEM_USSAGE_AVG} GB
    · MIN memory ussage: {MEM_USSAGE_MIN} GB
    · MAX memory ussage: {MEM_USSAGE_MAX} GB
· TOTAL network ussage (received): {NETWORK_USSAGE} MB
· TOTAL disk operations time: {DISK_USSAGE} seconds
· Duration of test (seconds): {RUN_TIME} seconds
        """ 

def __get_hw_info():
        """
        Gets hardware information and returns it as string
        """
        result = f"""
            · Platform : {platform.system()}
            · Architecture : {platform.machine()}
            · CPU : {platform.processor()}
            · RAM (GB) : {str(psutil.virtual_memory().total / (1024**3))}"""
        return result

def clean(*args):
    """
    This process is run when process is killed.
    We generate the report based on the hardware stats discovered
    while running the process.
    """
    #Compute final runtime
    REPORT_DATA['RUN_TIME'] = time.time() - REPORT_DATA['RUN_TIME']
    #Static fields
    result = REPORT_TEMPLATE.replace("{HARDWARE_CONFIGURATION}",__get_hw_info())
    result = result.replace("{MODEL_SELECTED}",REPORT_DATA['MODEL'])
    result = result.replace("{RUN_TIME}",str(f"{REPORT_DATA['RUN_TIME']:.2f}"))
    #CPU_STATS. 0 has no meaning here
    data = np.array(REPORT_DATA['CPU_PERCENT'])
    data[data != 0]
    result = result.replace("{CPU_LOAD_MAX}",str(f"{np.max(data):.2f}"))
    result = result.replace("{CPU_LOAD_MIN}",str(f"{np.min(data):.2f}"))
    result = result.replace("{CPU_LOAD_AVG}",str(f"{np.average(data):.2f}"))
    #Memory stats
    data = np.array(REPORT_DATA['MEMORY_USSAGE'])
    result = result.replace("{MEM_USSAGE_MAX}",str(f"{np.max(data):.2f}"))
    result = result.replace("{MEM_USSAGE_MIN}",str(f"{np.min(data):.2f}"))
    result = result.replace("{MEM_USSAGE_AVG}",str(f"{np.average(data):.2f}"))
    #Network max ussage
    data = np.array(REPORT_DATA['NETWORK_USSAGE'])
    result = result.replace("{NETWORK_USSAGE}",str(f"{np.max(data):.4f}"))
    #Disk max ussage
    data = np.array(REPORT_DATA['DISK_USSAGE'])
    result = result.replace("{DISK_USSAGE}",str(f"{np.max(data):.2f}"))
    #Write report to file
    with open(RESULT_FILE, "w") as my_file:
        my_file.write(result)
    sys.exit(0)

if __name__ == '__main__':
    #Sleep time is a parameter
    sleep_time = int(sys.argv[1])
    #Model is a parameter
    REPORT_DATA['MODEL'] = sys.argv[2]
    #Result file is a parameter
    RESULT_FILE = sys.argv[3]
    #Get process start time
    REPORT_DATA['RUN_TIME'] = time.time()
    #Initialize values for delta computing
    init_network = psutil.net_io_counters().bytes_recv / (1024**2)
    init_disk = (psutil.disk_io_counters().read_time + psutil.disk_io_counters().write_time) /1000
    #Initialize values for MAX MIN AVG
    REPORT_DATA['CPU_PERCENT'] = []
    REPORT_DATA['MEMORY_USSAGE'] = []
    REPORT_DATA['NETWORK_USSAGE'] = []
    REPORT_DATA['DISK_USSAGE'] = []
    while True:
        #Append values
        REPORT_DATA['CPU_PERCENT'].append(psutil.cpu_percent(percpu=False))
        REPORT_DATA['MEMORY_USSAGE'].append(psutil.virtual_memory().used /(1024**3))
        REPORT_DATA['NETWORK_USSAGE'].append(psutil.net_io_counters().bytes_recv / (1024**2) - init_network)
        REPORT_DATA['DISK_USSAGE'].append((psutil.disk_io_counters().read_time + psutil.disk_io_counters().write_time) /1000 - init_disk)
        for sig in TERMINATION_SIGNAL_SET:
            #Ersilia process sent a termination signal
            signal(sig, clean)
        time.sleep(sleep_time)
