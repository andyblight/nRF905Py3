#!/usr/bin/env python3

# import pigpio

class nrf905:
    """ A wrapper class around pigpio that drives an nRF905 device. """

    def __init__(self):
        pins = "fred"
        self.init(pins)

    def init(self, pins):
        print("init")

    def open(self, frequency, callback=None):
        if callback:
            print("open with callback:", frequency, callback)
            callback("Callback data")
        else:
            print("open:", frequency)

    def write(self, data):
        print("write", data)

    def close(self):
        print("close")
