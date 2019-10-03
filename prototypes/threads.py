#!/usr/bin/env python3

""" This file was created so that I could test queues, threads and callacks.
"""

import queue
import time
import threading


class ThreadTest:
    
    def __init__(self):
        self._input_queue = queue.Queue()
        self._input_thread = None
        self._callback_fn = None

    def register_callback(self, callback_fn):
        self._callback_fn = callback_fn

    def start(self):
        self._input_thread = threading.Thread(target=self._input_worker)
        self._input_thread.start()

    def send(self, message):
        while message:  # Contains something.
            packet = message[0:32]  # Put first 32 bytes into a packet.
            print("Posting packet: '", packet, "'")
            self._input_queue.put(packet)
            message = message[32:]

    def stop(self):
        # block until all tasks are done
        self._input_queue.join()
        # stop workers
        self._input_queue.put(None)
        # join thread
        self._input_thread.join()

    def _input_worker(self):
        while True:
            packet = self._input_queue.get()
            if packet is None:
                break
            self._send(packet)
            self._input_queue.task_done()

    def _send(self, packet):
        print("Sending packet: '", packet, "'")
        # simulate delay
        time.sleep(0.5)


class StateMachine:
    _STATE_STANDBY = 0
    _STATE_TRANSMITTING = 1
    _STATE_CARRIER_BUSY = 2
    _STATE_RECEIVING = 3
    _STATE_RECEIVED = 4
    _STATE_POWER_DOWN = 5
    
    def __init__(self):
        self._state = self._STATE_POWER_DOWN

    def print(self):
        print("Current state:", self._state)

    def next_state(self, next_state):
        if self._state == self._STATE_POWER_DOWN:
            

class Hardware:
    """ Simluate the device. """
    
    def __init__(self):
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._worker)
        self._thread.start()

    def stop(self):
        # join thread
        self._thread.join()

    def _worker(self):
        while True:
            packet = self._input_queue.get()
            if packet is None:
                break
            self._send(packet)
            self._input_queue.task_done()

    def _send(self, packet):
        print("Sending packet: '", packet, "'")
        # simulate delay
        time.sleep(0.5)




def my_callback():
    print("my_callback")
    


##### START HERE ####
print("Tests started")
my_class = ThreadTest()
my_class.register_callback(my_callback)
my_class.start()
for i in range(0, 5):
    message = "This is a long message that will be sent to test how the data is broken up into a number of 32 byte packets."
    message += str(i)
    my_class.send(message)
my_class.stop()
print("Tests finished.")
