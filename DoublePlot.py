# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 15:08:20 2022

@author: Robert
"""


import pyfirmata2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import iir_filter
import scipy.signal as signal
import time
# Realtime oscilloscope at a sampling rate of 100Hz
# It displays analog channel 0.
# You can plot multiple chnannels just by instantiating
# more RealtimePlotWindow instances and registering
# callbacks from the other channels.
# Copyright (c) 2018-2020, Bernd Porr <mail@berndporr.me.uk>
# see LICENSE file.

PORT = 'COM4'


# Creates a scrolling data display
class RealtimePlotWindow:

    def __init__(self):
        # create a plot window
        self.fig1, self.ax1 = plt.subplots()
        self.plotbuffer1 = np.zeros(500)
        self.line1, = self.ax1.plot(self.plotbuffer1)
        self.ax1.set_ylim(0, 1.5)
        self.ringbuffer1 = []
        # add any initialisation code here (filters etc)
        self.ani1 = animation.FuncAnimation(self.fig1, self.update1, interval=100)
        
        self.fig2, self.ax2 = plt.subplots()
        self.plotbuffer2 = np.zeros(500)
        self.line2, = self.ax.plot(self.plotbuffer)
        self.ax2.set_ylim(0, 1.5)
        self.ringbuffer2 = []
        # add any initialisation code here (filters etc)
        self.ani2 = animation.FuncAnimation(self.fig2, self.update2, interval=100)
        
        self.samplingRate = 50
        self.timestamp = 0
        self.board = pyfirmata2.Arduino('COM4')
        self.t_prev = 0
        self.fs_cal = 0
        self.fs_av = 0
        self.t_diff = 0
        self.counter = 0
        self.arr_size = 25
        self.fs_array = np.zeros(self.arr_size)
        
        self.t1 = self.ax1.text(1, 1.4,  str(round(self.fs_av,2)) + "Hz")
        self.t2 = self.ax2.text(1, 1.4,  str(round(self.fs_av,2)) + "Hz")
        
        self.sos = signal.butter(2,0.1 ,fs=self.samplingRate, output='sos') #2nd order,lowpass[this is default if not specified], 0.1Hz analogue (use analogue frequency when specifying the sampling rate )
        
    def start(self):
        self.board.analog[0].register_callback(self.Callback)
        self.board.samplingOn(1000 / self.samplingRate)
        self.board.analog[0].enable_reporting()    
        
    def stop(self):
        self.board.samplingOff()
        self.board.exit()    
        
    # updates the plot
    def update1(self, data):
        # add new data to the buffer
        self.plotbuffer1 = np.append(self.plotbuffer1, self.ringbuffer1)
        # only keep the 500 newest ones and discard the old ones
        self.plotbuffer1 = self.plotbuffer1[-500:]
        self.ringbuffer1 = []
        # set the new 500 points of channel 9
        self.line1.set_ydata(self.plotbuffer1)
        return self.line1
    
    def update2(self, data):
        # add new data to the buffer
        self.plotbuffer2 = np.append(self.plotbuffer2, self.ringbuffer2)
        # only keep the 500 newest ones and discard the old ones
        self.plotbuffer2 = self.plotbuffer1[-500:]
        self.ringbuffer2 = []
        # set the new 500 points of channel 9
        self.line1.set_ydata(self.plotbuffer2)
        return self.line2

    # appends data to the ringbuffer             self.ringbuffer.append(data)
    def Callback(self, data):
        self.ringbuffer1.append(data)
        self.ringbuffer2.append(self.Filter(data))
        self.counter += 1
        t_current = time.time()
        self.t_diff = t_current - self.t_prev
        self.SampleRateChecker(data)
        print("%f,%f,%f,%f,%f" % (self.timestamp, self.t_prev, t_current,self.t_diff, self.fs_av))
        self.t_prev = t_current 
        self.timestamp += (1 / self.samplingRate) 
        
    def Filter(self ,data):    
        f = iir_filter.IIR_filter(self.sos)
        filt_data = f.filter(data)
        return filt_data
        
    def SampleRateChecker(self, data): 
        if (self.t_diff <= 0):
            pass
        elif (self.t_diff > 0): 
            self.fs_cal = 1/self.t_diff
            self.fs_array[0] = self.fs_cal
            self.fs_array = np.roll(self.fs_array,1)
            if (self.counter % self.arr_size == 0):
                self.fs_av = np.mean(self.fs_array)  
                self.fs_array = np.zeros(self.arr_size)
                self.t1.set_text("fs = "+ str(round(self.fs_av,2)) + "Hz")
                
                         


# Create an instance of an animated scrolling window
# To plot more channels just create more instances and add callback handlers below
realtimePlotWindow1 = RealtimePlotWindow()
#realtimePlotWindow2 = RealtimePlotWindow()


#sos = signal.butter(2,0.1 ,fs=samplingRate, output='sos') #2nd order,lowpass[this is default if not specified], 0.1Hz analogue (use analogue frequency when specifying the sampling rate )
#f = iir_filter.IIR_filter(sos)

# Get the Ardunio board.
print("Let's print data from Arduino's analogue pins!")


# Let's create an instance

# and start DAQ
realtimePlotWindow1.start()

# show the plot and start the animation
plt.show()

realtimePlotWindow1.stop()

print("finished")

# needs to be called to close the serial port