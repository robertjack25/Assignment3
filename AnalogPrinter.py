# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 14:29:11 2022

@author: Robert
"""


# PORT = '/dev/ttyACM0'

# prints data on the screen at the sampling rate of 50Hz
# can easily be changed to saving data to a file

# It uses a callback operation so that timing is precise and
# the main program can just go to sleep.
# Copyright (c) 2018-2020, Bernd Porr <mail@berndporr.me.uk>
# see LICENSE file.

import pyfirmata2

import time

class AnalogPrinter:

    def __init__(self):
        # sampling rate: 10Hz (fs) #measures well at 10Hz
        self.samplingRate = 50 #cant calculate sampling rate at >35Hz
        self.timestamp = 0
        self.board = pyfirmata2.Arduino('COM4')
        self.timestamp_prevtime = time.time()
        self.timestamp_current = time.time()
        self.fs_cal = 0
        self.t_diff = 0

    def start(self):
        self.board.analog[0].register_callback(self.myPrintCallback)
        self.board.samplingOn(1000 / self.samplingRate)
        self.board.analog[0].enable_reporting()

#when putting time.time() as the last argument can see that the board doesnt sample at a perfect 10Hz
    def myPrintCallback(self, data):
        print("%f,%f,%f,%f" % (self.timestamp, data, self.fs_cal, self.t_diff)) #, self.t_diff
        self.timestamp += (1 / self.samplingRate) #okay
        self.timestamp_current = time.time()
        self.t_diff = self.timestamp_current - self.timestamp_prevtime
        self.timestamp_prevtime = self.timestamp_current #previously used time.time() here
        self.fs_cal = 1/self.t_diff

    def stop(self):
        self.board.samplingOff()
        self.board.exit()

print("Let's print data from Arduino's analogue pins!")


# Let's create an instance
analogPrinter = AnalogPrinter()

# and start DAQ
analogPrinter.start()

time.sleep(4)

analogPrinter.stop()

print("finished")
#analogPrinter.myPrintCallback(2)

#board.get_pin('a:0:i')

#could try time.time(ns)


