import KeithleyV16
import datetime
import numpy as np
import matplotlib.pyplot as plt
import os

keithley = KeithleyV16.KeithleyV16(1e-2, 'SPEED_NORMAL')
sweep_start = 0.0
sweep_end = 5.0
sweep_step = 0.2

sample_name = 'rGO100pc_no1_NPl'
time_for_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
path = './data/'
if not os.path.exists(path):
   os.makedirs(path)
   
filename = path + time_for_name + '_' + sample_name +'_IV_' + str(sweep_end)


column_names = []
data = []
column_names.append("Voltage (V)")
'''
voltages = np.empty(steps)
for i in range(steps):
    voltages[i] = sweep_start + (sweep_step * i)

data.append(voltages)
'''
print("Sample set name: ", sample_name)

while True:
    print('Enter sample label (or press Enter to finish): ')
    sample_num = input()
    if sample_num == "":
        break
    column_names.append(sample_num)
    [voltages, currents] = keithley.iv(sweep_start, sweep_end, sweep_step)
    if data == []:
        data.append(voltages)
    data.append(currents)
    KeithleyV16.iv2fig(filename, voltages, currents, ' ', showfig=True, savefig=False)
    plt.show()


np_data = np.stack(data, axis=0)    

delim = ','
column_names_str = delim.join(column_names)

KeithleyV16.data2file(filename, np_data, column_names)
#np.savetxt(filename + '.csv', np_data.T, fmt='%.10g', delimiter=',', header=column_names_str)

KeithleyV16.iv2fig(filename, np_data[0,:], np_data[1:,:], column_names[1:], showfig=True, savefig=True)

'''
By unknown reason iv2fig() does not show anything, but a figure is created. 
But the plot is appeared if plt.show() is called here, so plt.show!
'''

plt.show()