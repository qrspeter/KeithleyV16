from KeithleyV15 import SMU26xx
import matplotlib.pyplot as plt
import time
import datetime
import csv
import numpy as np

drain_start = 0.0
drain_end = -20.0
drain_step = 0.5
gate_bias = -20.0

sample_name = '1_p1'

if drain_start > drain_end:
    drain_step = -1 * np.abs(drain_step)
else:
    drain_step = np.abs(drain_step)
    
    
drain_steps = int((drain_end - drain_start) / drain_step)

current_range = 1e-6
current_range_for_name = str(current_range)

""" ******* Connect to the Sourcemeter ******** """

# initialize the Sourcemeter and connect to it
# you may need to change the IP address depending on which sourcemeter you are using
sm = SMU26xx('TCPIP0::192.166.1.101::INSTR') 

# get one channel of the Sourcemeter 
smu_drain = sm.get_channel(sm.CHANNEL_A)
smu_gate = sm.get_channel(sm.CHANNEL_B)


# reset to default settings
smu_drain.reset()
smu_gate.reset()
# setup the operation mode of the source meter to act as a voltage source - the SMU generates a voltage and measures the current
smu_drain.set_mode_voltage_source()
smu_gate.set_mode_voltage_source()
# set the voltage and current parameters
smu_drain.set_voltage_range(40)
smu_drain.set_voltage_limit(40)
smu_drain.set_voltage(0)
smu_drain.set_current_range(current_range)
smu_drain.set_current_limit(current_range)
smu_drain.set_current(0)

smu_gate.set_voltage_range(40)
smu_gate.set_voltage_limit(40)
smu_gate.set_voltage(0)
smu_gate.set_current_range(current_range)
smu_gate.set_current_limit(current_range)
smu_gate.set_current(0)

#smu_drain.set_measurement_speed_normal()
smu_drain.set_measurement_speed_hi_accuracy()
smu_gate.set_measurement_speed_hi_accuracy()
'''
40 измерений (20В по 0,25)
set_measurement_speed_hi_accuracy - 37 секунд (1.41859e-09 A)
set_measurement_speed_fast - 2 секунды (4.65035e-08 A)

SPEED_FAST / SPEED_MED / SPEED_NORMAL / SPEED_HI_ACCURACY
'''

""" ******* For saving the data ******** """

# Create unique filenames for saving the data
time_for_name = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
time_for_title = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

filename_csv = './data/' + 'FET_' + sample_name + '_' + time_for_name + '_vgs_' + str(gate_bias) + '.csv'

#initializing a CSV file, to which the measurement data will be written - if this script is used to measure another characteristic than the U/I curve, this has to be changed
# Header for csv
with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile,  lineterminator='\n')
        writer.writerow(["# Drain (V)", "Drain (A)", "Gate (V)", "Gate / A"])

""" ******* Make a voltage-sweep and do some measurements ******** """

# define variables we store the measurement in
drain_current = []
drain_voltage = []
gate_current = []

# enable the output
smu_drain.enable_output()
smu_gate.enable_output()


smu_gate.set_voltage(gate_bias)

# step through the voltages and get the values from the device
#for nr in range(1500):
for nr in range(drain_steps):
    # calculate the new voltage we want to set
    dr_voltage = drain_start + (drain_step * nr)
    # set the new voltage to the SMU
#    smu_drain.set_voltage(0.3)
    smu_drain.set_voltage(dr_voltage)
    # get current and voltage from the SMU and append it to the list so we can plot it later
    [current, voltage] = smu_drain.measure_current_and_voltage()
#    voltage = dr_voltage
    drain_voltage.append(voltage)
    drain_current.append(current)
    g_curr = smu_gate.measure_current()
    gate_current.append(g_curr)
    print(str(voltage)+'V; '+str(current)+' A; ' + str(g_curr) + ' A')
    # Write the data in a csv
    with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile,  lineterminator='\n')
        writer.writerow([voltage, current, gate_bias, g_curr])
       

# disable the output
smu_drain.disable_output()
smu_gate.disable_output()


# properly disconnect from the device
sm.disconnect()

""" ******* Plot the Data we obtained ******** """

plt.plot(drain_voltage, drain_current, label = r'$I_{DS}$', color='red', linewidth=2)
plt.plot(drain_voltage, gate_current, label = r'$I_{GS}$', color='black', linestyle='dashed', linewidth=1)

# set labels and a title
plt.xlabel('Voltage (V)', fontsize=14)
plt.ylabel('Current (A)', fontsize=14)
plt.title(time_for_title + r', $V_{GS}$ = ' + str(gate_bias), fontsize=14)
plt.tick_params(labelsize = 14)
plt.legend(loc = 'upper right')

plt.show()
