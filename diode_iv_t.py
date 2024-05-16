import KeithleyV16
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import csv

keithley = KeithleyV16.KeithleyV16(1e-3, 'SPEED_NORMAL')
sweep_start = 0.0
sweep_end = 2.0
sweep_step = 0.2
step = 2.0 # in sec. Not less than 0.7 for hi_accuracy and 0.5 for speed_normal

sample_name = 'rGO10_NPl_p1'
time_for_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
path = './data/'
if not os.path.exists(path):
   os.makedirs(path)
   
filename = path + time_for_name + '_' + sample_name +'_iv-t_' + str(sweep_end)



print("Sample set name: ", sample_name)


with open(filename + '.csv', 'a') as csvfile:
        writer = csv.writer(csvfile,  lineterminator='\n')
        writer.writerow(["# Time (sec)", "Drain (A)", "Drain (V)"])

current_log = []
time_log = []


plt.ion()  # enable interactivity
fig = plt.figure()  # make a figure
ax = fig.add_subplot(111)
line1, = ax.plot(time_log, current_log, 'r.')
#line1, = ax.plot(time_arr, drain_current, label = r'$I_{DS}$', color='red', linewidth=2)
plt.xlabel('Time / s', fontsize=14)
plt.ylabel('Current / A', fontsize=14)
plt.title(time_for_name + r', $V_{DS}$ = ' + str(sweep_end), fontsize=14)
plt.tick_params(labelsize = 14)

# to skip drawing of first dot (draws with a big delay)
line1.set_xdata(time_log)
line1.set_ydata(current_log)
ax.relim()
ax.autoscale()
fig.canvas.draw()
fig.canvas.flush_events()


try:
    start = time.time()

    while True:

        nt = time.time()

        while (nt - start) < (step * (len(time_log))):
            #print(f'{len(time_arr)=}, until next meas {-(nt - start) + (step * len(time_arr))}')
            nt = time.time() 
        steps_over = 2
        [voltages, currents] = keithley.iv(sweep_start, sweep_end + steps_over*sweep_step, sweep_step)
        aver = sum(currents[-2*steps_over-1:])/(2*steps_over + 1)
        current_log.append(currents[-1])
        time_log.append(nt - start)
        
        print('%.2f' % (nt - start), ' sec; ', currents[-1], ' A')
        # Write the data in a csv
        with open(filename + '.csv', 'a') as csvfile:
            writer = csv.writer(csvfile,  lineterminator='\n')
            writer.writerow(['%.3f' % (nt - start), currents[-1], sweep_end])

        line1.set_xdata(time_log)
        line1.set_ydata(current_log)
        ax.relim()
        ax.autoscale()
        fig.canvas.draw()
        fig.canvas.flush_events()



except KeyboardInterrupt:
    pass
    

plt.ioff()

KeithleyV16.it2fig(time_log, current_log, 'Time, s', filename, showfig=True, savefig=True)
plt.show()

