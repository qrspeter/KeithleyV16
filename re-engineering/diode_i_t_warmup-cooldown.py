from KeithleyV15 import SMU26xx
import matplotlib.pyplot as plt
import time
import datetime
import csv
#import winsound
import numpy as np

import time

sample_name = 'NPl_CdSe_p1_ns6'

drain_bias = 2.0 # V
interval = 1.0 # sec, errors if time is shorter than 0.5 for hi_accuracy and 0.001 for fast (but wrong print time)
# 0.01@fast works fine
# 
warmup_duration = 1000 # sec, Delay for warm-up
cooldown_duration = 4000

laser_periods = 10 # periods of acqusition for averaging
laser_period = 100 # sec, repetition period of laser pulses
laser_duration = 2  # sec, length of a single laser pulse
laser_delay = 1  # sec, pulse delay from the beginning of each period

current_range = 1e-2
# current_ranges = [1E-9, 1E-8, 1E-7, 1E-6, 1E-5, 1E-4, 1E-3, 1E-2, 1E-1, 1, 1.5]
current_limit = current_range

'''
Press Ctrl-C to terminate any loop.
'''
# it is better to move graphs to some thread because they block main function

def warm_up(duration, interval, filename, add_time=0):
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

        with open(filename, 'a') as csvfile:
            writer = csv.writer(csvfile,  lineterminator='\n')
            writer.writerow(['#Time(s)', 'Current(A)', 'Voltage(V)'])


        print('Waiting for {} seconds. Press Ctl+C to escape.'.format(duration))
        start_warm_up = time.time()
        nt = time.time()
        
        length = int(duration / interval)
        
        for i in range(length):

            while nt - start_warm_up < interval * i:
                nt = time.time()
                #print(f'{i=}, until next meas {interval * i - (nt - start_warm_up)}')  
                
            [current, voltage] = smu_drain.measure_current_and_voltage()
            print('%.4f' % (nt - start_warm_up + add_time),  '%.5e' % current, '%.2f' % voltage)
            with open(filename, 'a') as csvfile:
                writer = csv.writer(csvfile,  lineterminator='\n')
                writer.writerow(['%.3f' % (nt - start_warm_up + add_time), current, voltage])

#            data_raw[i] = current

            drain_current.append(current)
            time_arr.append(nt - start_warm_up + add_time)
            line1.set_xdata(time_arr)
            line1.set_ydata(drain_current)
            ax.relim()
            ax.autoscale()
            fig.canvas.draw()
            fig.canvas.flush_events()


        print('End of warm-up')
        plt.ioff()
        plt.close(fig)
        return(drain_current)

    except KeyboardInterrupt:
        plt.ioff()
        plt.close(fig)
        return(drain_current)
#        pass    

def acquisition(interval, periods, period, duration, delay, filename):
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

        start = time.time()
        
        laser_state = 0
        sm.write_lua("digio.writebit(1, 0)")
        #acq_length = (periods * period) / interval
        for p in range(periods):
            for i in range(int(period / interval)):
                nt = time.time()
                while nt - start - period * p < interval * i:
                    #print(f'{i=}, until next meas {interval * i - (nt - start)}')
                    nt = time.time()
                    
                if (i * interval < delay) or (i * interval > delay + duration): 
                    laser_state = 0
                    sm.write_lua("digio.writebit(1, {})".format(laser_state))
                else:
                    laser_state = 1
                    sm.write_lua("digio.writebit(1, {})".format(laser_state))
                    

                [current, voltage] = smu_drain.measure_current_and_voltage()
                print('%.4f' % (nt - start), '%.5e' % current, '%.2f' % voltage, 'laser_state=', laser_state)
                with open(filename, 'a') as csvfile:
                    writer = csv.writer(csvfile,  lineterminator='\n')
                    writer.writerow(['%.3f' % (nt - start), current, voltage])

                with open(filename[:-4] + '_meas' + '.csv', 'a') as csvfile:
                    writer = csv.writer(csvfile,  lineterminator='\n')
                    writer.writerow(['%.3f' % (nt - start), current, voltage])
            

                drain_current.append(current)
                time_arr.append(nt - start)
                line1.set_xdata(time_arr)
                line1.set_ydata(drain_current)
                ax.relim()
                ax.autoscale()
                fig.canvas.draw()
                fig.canvas.flush_events()



        sm.write_lua("digio.writebit(1, 0)")
        plt.ioff()
        plt.close(fig)

#        data2fig([time_arr, drain_current], ['t', 'I'], filename_raw[:-4] + '_meas' + '.png')
        return 
    
    except KeyboardInterrupt:
        sm.write_lua("digio.writebit(1, 0)")
        plt.ioff()
        plt.close(fig)
        data2fig([time_arr, drain_current], ['t', 'I'], filename_raw[:-4] + '_meas' + '.png')
        return

def lists2file(filename, lst, column_names=['t(c)', 'I(A)']):
#    lists2file(column_names_str, filename_raw, lst_raw)
    delim = ','
    column_names_str = delim.join(column_names)
    
    np_data = np.stack(lst, axis=0)

    np.savetxt(filename, np_data.T, fmt='%.10g', delimiter=delim, header=column_names_str) 

    
def data2fig(lst, column_names, filename, show=False, savefig=True):
    
    np_arr = np.stack(lst, axis=0)
    plt.figure(figsize=(8,6))
    for i in range(np_arr.shape[0]-1):
        plt.plot(np_arr[0, :], np_arr[i+1,:], label=column_names[i + 1], linewidth=2)
    plt.xlabel('Time (s)', fontsize=14)
    plt.ylabel('Current (A)', fontsize=14)
    plt.title(time_for_title, fontsize=14)
    plt.tick_params(labelsize=14)
    plt.legend() #loc='upper left')
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


print("Sample name: ", sample_name)
#sample_label = input()


it_warmup = np.array(warm_up(warmup_duration, interval, filename_raw, add_time=-warmup_duration))

timestamp = interval * np.array(range(len(it_warmup)))
timestamp =  timestamp - len(it_warmup) * interval

#    print(data_raw)
if len(it_warmup) != int(warmup_duration * interval):
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile,  lineterminator='\n')
        writer.writerow(['#Time(s)', 'Current(A)', 'Voltage(V)'])
    lists2file(filename_raw, [timestamp, it_warmup, it_warmup])

start_meas = time.time()
acquisition(interval, laser_periods, laser_period, laser_duration, laser_delay, filename_raw)


# sound alarm - end of accumulation
print('\a')
#winsound.Beep(1000, 300)

warm_up(cooldown_duration, interval, filename_raw, add_time=time.time()-start_meas)


it = np.loadtxt(filename_raw[:-4] + '_meas.csv', delimiter=',')
#data2fig([it[:,0], it[:,1]], ['t', 'I'], filename_raw[:-4] + '.png')
data2fig([it[:,0], it[:,1]], ['t', 'I'], filename_raw[:-4] + '_meas.png')

it = np.loadtxt(filename_raw, delimiter=',')
#data2fig([it[:,0], it[:,1]], ['t', 'I'], filename_raw[:-4] + '.png')
data2fig([it[:,0], it[:,1]], ['t', 'I'], filename_raw[:-4] + '.png', show=True)
