# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 16:12:02 2022

@author: Robert
"""


import pyfirmata2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

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
        self.fig, self.ax = plt.subplots()
        self.plotbuffer = np.zeros(500)
        self.line, = self.ax.plot(self.plotbuffer)
        self.ax.set_ylim(0, 1.5)
        self.ringbuffer = []
        # add any initialisation code here (filters etc)
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=100)
        
        self.samplingRate = 100
        self.timestamp = 0
        self.board = pyfirmata2.Arduino('COM4')
        self.t_prev = 0
        self.fs_cal = 0
        self.fs_av = 0
        self.t_diff = 0
        self.counter = 0
        self.arr_size = 50
        self.fs_array = np.zeros(self.arr_size)
        self.t1 = self.ax.text(0, 0,  str(round(self.fs_av,2)) + "Hz")
        
    def start(self):
        self.board.analog[0].register_callback(self.Callback)
        self.board.samplingOn(1000 / self.samplingRate)
        self.board.analog[0].enable_reporting()    
        
    def stop(self):
        self.board.samplingOff()
        self.board.exit()    
        
    # updates the plot
    def update(self, data):
        # add new data to the buffer
        self.plotbuffer = np.append(self.plotbuffer, self.ringbuffer)
        # only keep the 500 newest ones and discard the old ones
        self.plotbuffer = self.plotbuffer[-500:]
        self.ringbuffer = []
        # set the new 500 points of channel 9
        self.line.set_ydata(self.plotbuffer)
        return self.line

    # appends data to the ringbuffer             self.ringbuffer.append(data)
    def Callback(self, data):
        self.ringbuffer.append(data)
        self.counter += 1
        t_current = time.time()
        self.t_diff = t_current - self.t_prev
        self.SampleRateChecker(data)
        print("%f,%f,%f,%f,%f" % (self.timestamp, self.t_prev, t_current,self.t_diff, self.fs_av))
        self.t_prev = t_current #previously used time.time() here
        self.timestamp += (1 / self.samplingRate) 
        

        
    def SampleRateChecker(self, data): 
        if (self.t_diff == 0):
            pass
        elif (self.t_diff != 0): 
            self.fs_cal = 1/self.t_diff
            self.fs_array[0] = self.fs_cal
            self.fs_array = np.roll(self.fs_array,1)
            if (self.counter % self.arr_size == 0):
                self.fs_av = np.mean(self.fs_array)  
                self.fs_array = np.zeros(self.arr_size)
                self.t1.set_text(str(round(self.fs_av,2)) + "Hz")


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


