import KeithleyV16
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import csv
import os

from threading import Thread, Event


current_range = 1e-2
# current_ranges = [1E-9, 1E-8, 1E-7, 1E-6, 1E-5, 1E-4, 1E-3, 1E-2, 1E-1, 1, 1.5]
keithley = KeithleyV16.KeithleyV16(current_range, 'SPEED_NORMAL')
bias = 2 # V

step = 1.0 # in sec. Not less than 0.7 for hi_accuracy and 0.5 for speed_normal

sample_name = 'resistor' #'NPl_CdSe_p1'
path = './data/'

def read_input(q_entered_event):
    c = input()
    if c == "q":
        print("Breaking")
        q_entered_event.set()
        
        
def measurement_it(filename, step):
    '''
    comments...
    comments...
    '''
    with open(filename + '.csv', 'a') as csvfile:
            writer = csv.writer(csvfile,  lineterminator='\n')
            writer.writerow(["# Time (sec)", "Drain (A)", "Drain (V)"])

    fig = plt.figure()  # make a figure
    ax = fig.add_subplot(111)
    line1, = ax.plot(time_log, current_log, 'r.')
    #line1, = ax.plot(time_arr, drain_current, label = r'$I_{DS}$', color='red', linewidth=2)
    plt.xlabel('Time / s', fontsize=14)
    plt.ylabel('Current / A', fontsize=14)
    plt.title(time_for_name + r', $V_{DS}$ = ' + str(bias), fontsize=14)
    plt.tick_params(labelsize = 14)

    # to skip drawing of first dot (draws with a big delay)
    line1.set_xdata(time_log)
    line1.set_ydata(current_log)
    ax.relim()
    ax.autoscale()
    fig.canvas.draw()
    fig.canvas.flush_events()
    keithley.set_v(bias)
    keithley.get_v()

    current_log = []
    time_log = []

    q_pressed_event = Event()
    input_thread = Thread(target=read_input, daemon=True, args=(q_pressed_event,))
    input_thread.start()
    
    start = time.time()
    
    while True:

        nt = time.time()

        while (nt - start) < (step * (len(time_log))):
            #print(f'{len(time_arr)=}, until next meas {-(nt - start) + (step * len(time_arr))}')
            nt = time.time() 
        [current, voltage] = keithley.get_i_v()
        current_log.append(current)
        time_log.append(nt - start)
        
        print('%.2f' % (nt - start), ' sec; ', current, ' A')
        # Write the data in a csv
        with open(filename + '.csv', 'a') as csvfile:
            writer = csv.writer(csvfile,  lineterminator='\n')
            writer.writerow(['%.3f' % (nt - start), current, bias])

        line1.set_xdata(time_log)
        line1.set_ydata(current_log)
        ax.relim()
        ax.autoscale()
        fig.canvas.draw()
        fig.canvas.flush_events()

        if q_pressed_event.is_set():
            break


if not os.path.exists(path):
   os.makedirs(path)
   
filename = path + time_for_name + '_' + sample_name +'_it_' + str(bias)

print("Sample name: ", sample_name)

time_for_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

plt.ion()  # enable interactivity
measurement_it(filename, step)


plt.ioff()
    
#plt.pause(100)
plt.close("all")

keithley.disable()


recorded = np.loadtxt(filename + '.csv', delimiter=',')

KeithleyV16.it2fig(filename, recorded[:,0], recorded[:,1], ['Time, s'], showfig=True, savefig=True)
plt.show()