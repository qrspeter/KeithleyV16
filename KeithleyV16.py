# KeithleyV16.py
# wrapper for KeithleyV15.py with IV measurement.

import numpy as np
import datetime
import os

import KeithleyV15

import matplotlib.pyplot as plt

from dataclasses import dataclass


@dataclass
class KeithleyV16(object):
    __i_range     : float
    __accuracy    : str
    __begin       : float
    __end         : float
    __step        : float

    voltage_range = 40
    voltage_limit = voltage_range
    accuracy_set = {'SPEED_FAST', 'SPEED_MED', 'SPEED_NORMAL', 'SPEED_HI_ACCURACY'}
    
    def __init__(self, __i_range = 1e-3, __accuracy = 'SPEED_NORMAL'):
        assert __i_range >= 1e-9 and __i_range <= 1.5

        self.current_range = __i_range
        # current_ranges = [1E-9, 1E-8, 1E-7, 1E-6, 1E-5, 1E-4, 1E-3, 1E-2, 1E-1, 1, 1.5]
        self.current_limit = self.current_range
        self.sm = KeithleyV15.SMU26xx('USB0::0x05E6::0x2636::4097970::INSTR') #('TCPIP0::192.166.1.101::INSTR') 
        self.smu_drain = self.sm.get_channel(self.sm.CHANNEL_A)

        self.smu_drain.reset()

        self.smu_drain.set_mode_voltage_source()
        self.smu_drain.set_voltage_range(self.voltage_range)
        self.smu_drain.set_voltage_limit(self.voltage_limit)
        self.smu_drain.set_voltage(0)
        self.smu_drain.set_current(0)

        if self.current_range == 0:
            self.smu_drain.enable_current_autorange()      # it is not working
        else:
            self.smu_drain.set_current_range(self.current_range)
            self.smu_drain.set_current_limit(self.current_limit)
    
        assert __accuracy in self.accuracy_set
        match __accuracy:
            case 'SPEED_FAST':
                 self.smu_drain.set_measurement_speed_fast()
            case 'SPEED_MED':
                 self.smu_drain.set_measurement_speed_med()
            case 'SPEED_NORMAL':
                 self.smu_drain.set_measurement_speed_normal()
            case 'SPEED_HI_ACCURACY':
                 self.smu_drain.set_measurement_speed_hi_accuracy()
            case _:
                 self.smu_drain.set_measurement_speed_normal()
                                  
    def set_v(self,voltage):
        self.smu_drain.set_voltage(voltage)
    
    def get_v(self):
        return self.smu_drain.measure_voltage()
    
    def get_i_v(self):
        return self.smu_drain.measure_current_and_voltage()

    
    def iv(self, __begin = 0.0, __end = 5.0, __step = 0.2) -> [list, list]:
        assert __begin >= -1 * self.voltage_range and __begin <= self.voltage_range
        assert __end >= -1 * self.voltage_range and __end <= self.voltage_range
        assert __step >= -1 * self.voltage_range and __step <= self.voltage_range
        
        if __begin > __end:
            __step = -1 * np.abs(__step)
        else:
            __step = np.abs(__step)        
        

        self.smu_drain.enable_output()
        self.smu_drain.set_voltage(__begin)
        self.smu_drain.measure_current_and_voltage()

        steps = int((__end - __begin) / __step) + 1
        currents = np.zeros(steps)
        voltages = np.empty(steps)
        for i in range(steps):
            voltages[i] = __begin + (__step * i)
            
        # additional measurement to exclude error of first measurement
        self.smu_drain.set_voltage(voltages[0])
        [current, voltage] = self.smu_drain.measure_current_and_voltage()

        for nr in range(steps):
            self.smu_drain.set_voltage(voltages[nr])
            [current, voltage] = self.smu_drain.measure_current_and_voltage()
            currents[nr] = current
            #print(str('%.2f' % voltage) +' V; '+str('%.5e' % current)+' A')
        
        self.smu_drain.set_voltage(0)
        # disable the output
        self.smu_drain.disable_output()
        
        return [voltages, currents]

    def __del__(self):
        #self.smu_drain.disable_output()
        self.sm.disconnect()
        pass

        
def it(__step=1.0, duration=1000):
        return 0
        
def it_from_iv():
        return 0    

def pulsed(warm_up, duration, cool_down, __step):
        return 0

def iv2fig(filename, current, voltage, column_names=' ', showfig=False, savefig=True):
    data2fig(filename, current, voltage, column_names, 'Voltage (V)', 'Current (A)', showfig, savefig)
    
def it2fig(filename, times, current, column_names=' ', showfig=False, savefig=True):
    data2fig(filename, times, np.array(current), column_names, 'Time (s)', 'Current (A)', showfig, savefig)    

def data2fig(filename, x, y, column_names, x_name, y_name, showfig=False, savefig=True):
    
    fig = plt.figure(figsize=(8,6))
    if len(y.shape) == 1:
        plt.plot(x, y, label=str(*column_names), linewidth=2)
    else:
        for i in range(y.shape[0]):
            plt.plot(x, y[i,:], label=column_names[i], linewidth=2)

    plt.xlabel(x_name, fontsize=14)
    plt.ylabel(y_name, fontsize=14)
    time_for_title = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    plt.title(time_for_title, fontsize=14)
    plt.tick_params(labelsize = 14)
    plt.legend() #(loc='upper left')
    if savefig == True:
        plt.savefig(filename + '.png')
    if showfig == True:
        plt.show()


def data2file(filename, data, column_names=[]):
#    lists2file(column_names_str, filename_raw, lst_raw)
    delim = ','
    column_names_str = delim.join(column_names)
    np.savetxt(filename + '.csv', data, fmt='%.10g', delimiter=delim, header=column_names_str) 


    
if __name__ == "__main__":

    path = './data/'
    if not os.path.exists(path):
       os.makedirs(path)

    keithley = KeithleyV16(1e-3, 'SPEED_NORMAL')
    [voltages, currents] = keithley.iv(0.0, 1.0, 0.2) # 
    sweep_end = 5.0
    sample_name = 'rGO_10pc'
    time_for_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = './data/'
    filename = path + time_for_name + '_' + sample_name +'_IV_' + str(sweep_end)

    column_names = ('V','I')
    iv2fig(filename, voltages, currents, column_names[1:], True, True)
    data2file(filename, np.stack((voltages, currents), axis=0).T, column_names)
    # np.savetxt(filename + '.csv', np.stack((voltages, currents), axis=0).T, fmt='%.10g', delimiter=',', header='Voltage (V), ' + column_names)
    
