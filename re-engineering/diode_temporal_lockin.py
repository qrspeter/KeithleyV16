# для измерения напряжения на резисторе не подавая не него смещение от Кейтли, тк на него и так подается переменное напряжение, а сигнал снимается с выхода синхронного детектора

from KeithleyV15 import SMU26xx
import matplotlib.pyplot as plt
import time
import datetime
import csv
import numpy as np

sample_name = 'rGO_px1'

#drain_bias = 1.0


current_range = 1e-8
current_range_for_name = str(current_range)

""" ******* Connect to the Sourcemeter ******** """

# initialize the Sourcemeter and connect to it
# you may need to change the IP address depending on which sourcemeter you are using
sm = SMU26xx('TCPIP0::192.166.1.101::INSTR') 

# get one channel of the Sourcemeter 
smu_drain = sm.get_channel(sm.CHANNEL_A)

# reset to default settings
smu_drain.reset()
# setup the operation mode of the source meter to act as a voltage source - the SMU generates a voltage and measures the current
smu_drain.set_mode_voltage_source()
# set the voltage and current parameters
smu_drain.set_voltage_range(40)
smu_drain.set_voltage_limit(40)
#smu_drain.set_voltage(0)
smu_drain.set_current_range(current_range)
smu_drain.set_current_limit(current_range)
#smu_drain.set_current(0)

smu_drain.set_measurement_speed_hi_accuracy()
#smu_drain.set_measurement_speed_hi_accuracy()

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

filename_csv = './data/' + 'V_T_' + sample_name + '_' + time_for_name + '.csv'

#initializing a CSV file, to which the measurement data will be written - if this script is used to measure another characteristic than the U/I curve, this has to be changed
# Header for csv
with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile,  lineterminator='\n')
        writer.writerow(["# Time / sec", "Drain / V"])


# define variables we store the measurement in
drain_voltage = []
time_arr = []

# enable the output
smu_drain.enable_output()

plt.ion()  # enable interactivity
fig = plt.figure()  # make a figure
ax = fig.add_subplot(111)
line1, = ax.plot(time_arr, drain_voltage, 'r.')
#line1, = ax.plot(time_arr, drain_current, label = r'$I_{DS}$', color='red', linewidth=2)
plt.xlabel('Time / s', fontsize=14)
plt.ylabel('Voltage / V', fontsize=14)
plt.title(time_for_title, fontsize=14)
plt.tick_params(labelsize = 14)

#smu_drain.set_voltage(drain_bias)
# to skip the first measurement
#smu_drain.measure_current_and_voltage()

    
start = time.time()
# step through the voltages and get the values from the device


try:
    while True:

        voltage = smu_drain.measure_voltage()
        drain_voltage.append(voltage)
        
        t = time.time() - start
        time_arr.append(t)
        
        print(str(t)+ ' sec; '+str(voltage)+' V')
        # Write the data in a csv
        with open(filename_csv, 'a') as csvfile:
            writer = csv.writer(csvfile,  lineterminator='\n')
            writer.writerow([t, voltage])

        line1.set_xdata(time_arr)
        line1.set_ydata(drain_voltage)
        ax.relim()
        ax.autoscale()
        fig.canvas.draw()
        fig.canvas.flush_events()

except KeyboardInterrupt:
    smu_drain.disable_output()


# properly disconnect from the device
smu_drain.disable_output()
sm.disconnect()

plt.ioff()
plt.show()
