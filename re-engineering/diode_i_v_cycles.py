from KeithleyV15 import SMU26xx
import matplotlib.pyplot as plt
import time
import datetime
import csv
import numpy as np

sample_name = 'rGO_10pc_p4_before5Exp'

# define sweep parameters

sweep_start = 0.0
sweep_end = 2.0
sweep_step = 0.2


interval = 2
laser_start = 100
laser_duration = 10
cooldown = 100

'''
interval = 1
laser_start = 4
laser_duration = 4
cooldown = 3
'''
'''
interval = 10
laser_start = 30
laser_duration = 100
cooldown = 600
'''


current_range = 1e-4
# current_ranges = [1E-9, 1E-8, 1E-7, 1E-6, 1E-5, 1E-4, 1E-3, 1E-2, 1E-1, 1, 1.5]
current_limit = current_range
if current_limit > current_range:
    current_limit = current_range


if sweep_start > sweep_end:
    sweep_step = -1 * np.abs(sweep_step)
else:
    sweep_step = np.abs(sweep_step)
    
steps = int((sweep_end - sweep_start) / sweep_step) + 1


""" ******* Connect to the Sourcemeter ******** """

# initialize the Sourcemeter and connect to it
# you may need to change the IP address depending on which sourcemeter you are using
sm = SMU26xx('TCPIP0::192.166.1.101::INSTR') 

# get one channel of the Sourcemeter (we only need one for this measurement)
smu = sm.get_channel(sm.CHANNEL_A)

""" ******* Configure the SMU Channel A ******** """
#define a variable "current range" to be able to change it quickly for future measurements




# reset to default settings
smu.reset()
# setup the operation mode of the source meter to act as a voltage source - the SMU generates a voltage and measures the current
smu.set_mode_voltage_source()
# set the voltage and current parameters
smu.set_voltage_range(40)
smu.set_voltage_limit(40)
#smu.set_voltage(0)

#smu.set_current_limit(current_limit)
if current_range == 0:
    smu.enable_current_autorange()
else:
    smu.set_current_range(current_range)
    smu.set_current_limit(current_limit)

#smu.set_current(0)

#smu.set_measurement_speed_fast()
smu.set_measurement_speed_normal()
#smu.set_measurement_speed_hi_accuracy()
'''
40 измерений (20В по 0.25)
set_measurement_speed_hi_accuracy - 37 секунд (1.41859e-09 A)
set_measurement_speed_fast - 2 секунды (4.65035e-08 A)

SPEED_FAST / SPEED_MED / SPEED_NORMAL / SPEED_HI_ACCURACY
'''

""" ******* For saving the data ******** """


# Create unique filenames for saving the data
time_for_name = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
time_for_title = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
filename_csv = './data/' + time_for_name + '_' + sample_name +'_IV_' + str(sweep_end) + '.csv'

""" ******* Make a voltage-sweep and do some measurements ******** """

# enable the output
smu.enable_output()

smu.set_voltage(sweep_start)
smu.measure_current_and_voltage()

#smu.set_voltage(sweep_start)
#smu.measure_current_and_voltage()

# switch the laser off
sm.write_lua("digio.writebit(1, 0)")

# define variables we store the measurement in
column_names = []
data = []

voltages = np.empty(steps)
for i in range(steps):
    voltages[i] = sweep_start + (sweep_step * i)
column_names.append("Voltage (V)")
#column_names += "Voltage (V)"

data.append(voltages)

duration = laser_start + laser_duration + cooldown



plt.ion()  # enable interactivity
fig = plt.figure()  # make a figure
ax = fig.add_subplot(111)
line1, = ax.plot([0], [0], 'r.')
#line1, = ax.plot(time_arr, drain_current, label = r'$I_{DS}$', color='red', linewidth=2)
plt.xlabel('Time / s', fontsize=14)
plt.ylabel('Current / A', fontsize=14)
plt.title(time_for_title + r', $V_{bias}$ = ' + str(sweep_end), fontsize=14)
plt.tick_params(labelsize = 14)
'''
# to skip drawing of first dot (draws with a big delay)
line1.set_xdata(0)
line1.set_ydata(0)
ax.relim()
ax.autoscale()
fig.canvas.draw()
fig.canvas.flush_events()
'''

corrent_log = []
time_log = []

with open(filename_csv[:-4] + '_it.csv', 'a') as csvfile:
    writer = csv.writer(csvfile,  lineterminator='\n')
    writer.writerow(['#Time (s)', 'Current (A)'])

start_meas = time.time()
nt = time.time()

for meas in range(duration // interval):

    while nt - start_meas < interval * meas:
        #print(f'{i=}, until next meas {interval * i - (nt - start_pulse)}')
        nt = time.time()

    if (meas > laser_start//interval) and (meas <= (laser_start + laser_duration)//interval):
        sm.write_lua("digio.writebit(1, 1)")
    else:
        sm.write_lua("digio.writebit(1, 0)")

    current_time = interval * meas
    time_log.append(current_time)
    column_names.append(str(current_time))
    currents = np.zeros(steps)
    
    # additional measurement to exclude error of first measurement
    smu.set_voltage(voltages[0])
    [current, voltage] = smu.measure_current_and_voltage()

    for nr in range(steps):
        # calculate the new voltage we want to set
        # set the new voltage to the SMU
        smu.set_voltage(voltages[nr])
        # get current and voltage from the SMU and append it to the list so we can plot it later
        [current, voltage] = smu.measure_current_and_voltage()
        currents[nr] = current
        if nr == steps - 1:
            averaging = 4
            for i in range(averaging - 1):
                [current, voltage] = smu.measure_current_and_voltage()
                currents[nr] += current
            currents[nr] /= averaging
    
    smu.set_voltage(voltages[0])
    data.append(currents) 
    corrent_log.append(currents[-1])
    print('measurement ', meas + 1, '/', duration // interval, ', I = ', '%.6e' % currents[-1])
    with open(filename_csv[:-4] + '_it.csv', 'a') as csvfile:
        writer = csv.writer(csvfile,  lineterminator='\n')
        writer.writerow([meas * interval, currents[-1]])

    line1.set_xdata(time_log)
    line1.set_ydata(corrent_log)
    ax.relim()
    ax.autoscale()
    fig.canvas.draw()
    fig.canvas.flush_events()

#    time.sleep(interval)

plt.ioff()

np_data = np.stack(data, axis=0)    

delim = ','
column_names_str = delim.join(column_names)
np.savetxt(filename_csv, np_data.T, fmt='%.10g', delimiter=',', header=column_names_str)  

# disable the output
smu.disable_output()

# properly disconnect from the device
sm.disconnect()

""" ******* Plot the Data we obtained ******** """
fig = plt.figure(figsize=(8,6))
plt.plot([i * interval for i in range(np_data.shape[0]-1)], np_data[1:,-1]) # 
plt.xlabel('Time (s)', fontsize=14)
plt.ylabel('Current (A)', fontsize=14)
plt.title(time_for_title, fontsize=14)
plt.tick_params(labelsize=14)
#plt.legend() # (loc='upper left')
plt.savefig(filename_csv[:-4] + '_it.png')


fig = plt.figure(figsize=(8,6))
for i in range(np_data.shape[0]-1):
    plt.plot(np_data[0, :], np_data[i+1,:], label=column_names[i+1], linewidth=1) # 
plt.xlabel('Voltage (V)', fontsize=14)
plt.ylabel('Current (A)', fontsize=14)
plt.title(time_for_title, fontsize=14)
plt.tick_params(labelsize=14)
#plt.legend() # (loc='upper left')
plt.savefig(filename_csv[:-4] + '.png')
plt.show()

