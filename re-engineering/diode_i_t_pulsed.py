from KeithleyV15 import SMU26xx
import matplotlib.pyplot as plt
import time
import datetime
import csv
import winsound
import numpy as np

import time

sample_name = 'NPl_CdSe_p5_ns7'

drain_bias = 2.0 # V
interval = 1.0 # sec, errors if time is shorter than 0.5 for hi_accuracy and 0.001 for fast (but wrong print time)
# 0.01@fast works fine
# 
warmup_duration = 10 # sec, Delay for warm-up
cooldown_duration = 0

laser_periods = 4 # periods of acqusition for averaging
laser_period = 200 # sec, repetition period of laser pulses
laser_duration = 40  # sec, length of a single laser pulse
laser_delay = 5  # sec, pulse delay from the beginning of each period

current_range = 1e-2
# current_ranges = [1E-9, 1E-8, 1E-7, 1E-6, 1E-5, 1E-4, 1E-3, 1E-2, 1E-1, 1, 1.5]
current_limit = current_range

'''
Press Ctrl-C to terminate any loop.
'''
# it is better to move graphs to some thread because they block main function

def warm_up(duration, interval):
    try:

        drain_current = []
        time_arr = []
        plt.ion()  # enable interactivity
        fig = plt.figure()  # make a figure
        ax = fig.add_subplot(111)
        line1, = ax.plot(time_arr, drain_current, 'r.')
        #line1, = ax.plot(time_arr, drain_current, label = r'$I_{DS}$', color='red', linewidth=2)
        plt.xlabel('Time / s', fontsize=14)
        plt.ylabel('Current / A', fontsize=14)
#        plt.title(time_for_title + r', $V_{DS}$ = ' + str(drain_bias), fontsize=14)
        plt.tick_params(labelsize = 14)

        # to skip drawing of first dot (draws with a big delay)
        line1.set_xdata(time_arr)
        line1.set_ydata(drain_current)
        ax.relim()
        ax.autoscale()
        fig.canvas.draw()
        fig.canvas.flush_events()



        print('Waiting for warm-up for {} seconds. Press Ctl+C to escape.'.format(duration))
        start_warm_up = time.time()
        nt = time.time()
        
        length = int(duration / interval)
        
        for i in range(length):

            while nt - start_warm_up < interval * i:
                nt = time.time()
                #print(f'{i=}, until next meas {interval * i - (nt - start_warm_up)}')  
                
            [current, voltage] = smu_drain.measure_current_and_voltage()
            print('%.4f' % (nt - start_warm_up),  '%.5e' % current, '%.2f' % voltage)
#            data_raw[i] = current

            drain_current.append(current)
            time_arr.append(nt - start_warm_up)
            line1.set_xdata(time_arr)
            line1.set_ydata(drain_current)
            ax.relim()
            ax.autoscale()
            fig.canvas.draw()
            fig.canvas.flush_events()


        print('End of warm-up')
        plt.ioff()
        return(drain_current)

    except KeyboardInterrupt:
        plt.ioff()
        return(drain_current)
#        pass    

def acquisition(start_meas, arr, data_raw, offset):
    start_pulse = time.time()
    nt = time.time()
    laser_state = 0
    sm.write_lua("digio.writebit(1, 0)")
    
    for i in range(arr.size):
        while nt - start_pulse < interval * i:
            #print(f'{i=}, until next meas {interval * i - (nt - start_pulse)}')
            nt = time.time()
            
        if (i * interval < laser_delay) or (i * interval > laser_delay + laser_duration): 
            laser_state = 0
            sm.write_lua("digio.writebit(1, {})".format(laser_state))
        else:
            laser_state = 1
            sm.write_lua("digio.writebit(1, {})".format(laser_state))
            

        [current, voltage] = smu_drain.measure_current_and_voltage()
        print('%.4f' % (nt - start_pulse), '%.5e' % current, '%.2f' % voltage, 'laser_state=', laser_state)
        arr[i] = current
        data_raw[i + offset] = current
   
    sm.write_lua("digio.writebit(1, 0)")

def lists2file(column_names, filename, lst):
#    lists2file(column_names_str, filename_raw, lst_raw)
    delim = ','
    column_names_str = delim.join(column_names)
    
    np_data = np.stack(lst, axis=0)

    np.savetxt(filename, np_data.T, fmt='%.10g', delimiter=delim, header=column_names_str) 

    
def data2fig(lst, column_names, filename, show=False, savefig=True):
    
    np_arr = np.stack(lst, axis=0)
    fig = plt.figure(figsize=(8,6))
    for i in range(np_arr.shape[0]-1):
        plt.plot(np_arr[0, :], np_arr[i+1,:], label=column_names[i + 1], linewidth=2)
    plt.xlabel('Time (s)', fontsize=14)
    plt.ylabel('Current (A)', fontsize=14)
    plt.title(time_for_title, fontsize=14)
    plt.tick_params(labelsize = 14)
    plt.legend(loc='upper left')
    if savefig == True:
        plt.savefig(filename)
    if show == True:
        plt.show()
    
""" ******* Connect to the Sourcemeter ******** """

# initialize the Sourcemeter and connect to it
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
smu_drain.set_voltage(0)
smu_drain.set_current_range(current_range)
smu_drain.set_current_limit(current_limit)
smu_drain.set_current(0)

smu_drain.set_measurement_speed_hi_accuracy()

'''
40 measurements (20В по 0.25) take time:
set_measurement_speed_hi_accuracy - 37 sec (1.41859e-09 A)
set_measurement_speed_fast - 2 sec (4.65035e-08 A, less precision)

SPEED_FAST / SPEED_MED / SPEED_NORMAL / SPEED_HI_ACCURACY
'''

""" ******* For saving the data ******** """

# Create unique filenames for saving the data
time_for_name = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
time_for_title = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
filename_av = './data/' + 'PhotoCond_' + time_for_name + '_'  + sample_name + '_vds_' + str(drain_bias) +  '_cycles_' + str(laser_periods) + '.csv'
filename_raw = './data/' + 'PhotoCond_' + time_for_name + '_'  + sample_name + '_raw' + '.csv'

""" ******* Do some measurements ******** """


# enable the output
smu_drain.enable_output()

# switch the laser off
sm.write_lua("digio.writebit(1, 0)")


smu_drain.set_voltage(drain_bias)

# check timing conditions
if laser_period < laser_duration + laser_delay:
    print("Check timing parameters - laser_period, laser_duration and laser_delay")
    exit()

period_length = int(laser_period / interval)
warmup_length = int(warmup_duration / interval)
cooldown_length = int(cooldown_duration / interval)
data_raw_length = warmup_length + period_length * laser_periods + cooldown_length

data_accum = np.zeros(period_length)
data_raw = np.zeros(data_raw_length)

timestamp_accum =  interval * np.array(range(period_length))
timestamp_raw = interval * np.array(range(data_raw_length))

# define variables we store the measurement in
column_names = []
lst_accum = []
lst_raw = []

column_names.append("Time (sec)")

lst_accum.append(timestamp_accum)
lst_raw.append(timestamp_raw)

print("Samples set name: ", sample_name)

while True:
    print('Enter sample label (or press Enter to finish): ')
    sample_label = input()
    if sample_label == "":
        break

#    data_acum.fill(0.0)
#    data_raw.fill(0.0)
    
    column_names.append(sample_label)
    data_acq = np.zeros(period_length)
    
    lst_accum.append(data_accum.copy())
    lst_raw.append(data_raw.copy())

    start_meas = time.time()
    it_warmup = np.array(warm_up(warmup_duration, interval))
    
#    zer = np.where(w == 0.0)[0][0]
#    print(zer, warmup_length)
#    print(w)
    shift = warmup_length - len(it_warmup)
    #if shift > 0:
    lst_raw[-1][shift : (shift + len(it_warmup))] = it_warmup # np.roll(data_raw, warmup_length - zer)
#    print(data_raw)
    lists2file(column_names, filename_raw, lst_raw)

    plt.ion()  # enable interactivity


    try:
        fig = plt.figure()  # make a figure
        ax = fig.add_subplot(111)
        line1, = ax.plot(timestamp_accum, lst_accum[-1], color='blue', linewidth=2)
        plt.xlabel('Time / s', fontsize=14)
        plt.ylabel('Current / A', fontsize=14)
        plt.title(time_for_title, fontsize=14)
        plt.tick_params(labelsize = 14)
        
        print('Measurement started. Press Ctl+C to escape')
        for i in range(laser_periods):
            offset = warmup_length + i * period_length
            acquisition(start_meas, data_acq, lst_raw[-1], offset)
            
            print('Cycle ', i + 1, ' from ', laser_periods)

            lst_accum[-1] += data_acq
                        
            line1.set_xdata(timestamp_accum)
            line1.set_ydata(lst_accum[-1] / (i + 1))
            ax.relim()
            ax.autoscale()
            fig.canvas.draw()
            #plt.pause(0.001)
            fig.canvas.flush_events()

    except KeyboardInterrupt:
        sm.write_lua("digio.writebit(1,0)")

    plt.ioff()

    lst_accum[-1] = lst_accum[-1] / laser_periods
    
    

    lists2file(column_names, filename_av, lst_accum)
    lists2file(column_names, filename_raw, lst_raw)
    '''    
    np_data_accum   = np.stack(lst_accum, axis=0)
    np_data_raw     = np.stack(lst_raw, axis=0)
    
    np.savetxt(filename_av, np_data_accum.T, fmt='%.10g', delimiter=',', header=column_names_str) 

    np.savetxt(filename_raw, np_data_raw.T, fmt='%.10g', delimiter=",", header = column_names_str)
    '''
    
    '''
    plt.plot(timestamp_accum, data_accum, label = sample_label, color='red', linewidth=2)
    plt.xlabel('Time (sec)', fontsize=14)
    plt.ylabel('Current (A)', fontsize=14)
    plt.title(time_for_title + r', $Periods$ = ' + str(laser_periods) + r', $V$ = ' + str(drain_bias), fontsize=14)
    plt.tick_params(labelsize = 14)
    plt.legend(loc = 'upper right')
    plt.show()
    '''
    
    it_cooldown = np.array(warm_up(warmup_duration, interval))
    cooldown_start = warmup_length + period_length * laser_periods
    lst_raw[-1][cooldown_start : (cooldown_start + len(it_cooldown))] = it_cooldown
    
    data2fig([timestamp_accum, lst_accum[-1]], [column_names[0], column_names[-1]], 0,  savefig=False, show=True)
    
    # sound alarm - end of accumulation
    #print('\a')
    winsound.Beep(1000, 300)


data2fig(lst_raw, column_names, filename_raw[:-4] + '.png')
data2fig(lst_accum, column_names, filename_av[:-4] + '.png', show=True)
'''    
fig = plt.figure(figsize=(8,6))
for i in range(np_data_raw.shape[0]-1):
    plt.plot(np_data_raw[0, :], np_data_raw[i+1,:], label = column_names[i + 1], linewidth=2)
plt.xlabel('Time (s)', fontsize=14)
plt.ylabel('Current (A)', fontsize=14)
plt.title(time_for_title, fontsize=14)
plt.tick_params(labelsize = 14)
plt.legend(loc='upper left')
plt.savefig(filename_raw[:-4] + '.png')

fig = plt.figure(figsize=(8,6))
for i in range(np_data_accum.shape[0]-1):
    plt.plot(np_data_accum[0, :], np_data_accum[i+1,:], label = column_names[i + 1], linewidth=2)
plt.xlabel('Time (s)', fontsize=14)
plt.ylabel('Current (A)', fontsize=14)
plt.title(time_for_title, fontsize=14)
plt.tick_params(labelsize = 14)
plt.legend(loc='upper left')
plt.savefig(filename_av[:-4] + '.png')
plt.show()
'''
