#!/usr/bin/env python3

""" This file was created so that I could test queues, threads and callacks.
"""

import queue
import time
import threading


class ThreadTest:

    def __init__(self):
        self._input_queue = queue.Queue(100)
        self._input_thread = None
        self._callback_fn = None
        # self._busy_cv = threading.Condition()
        self._sending = False

    def register_callback(self, callback_fn):
        self._callback_fn = callback_fn

    def start(self):
        self._input_thread = threading.Thread(target=self._input_worker,
                                              name="Input")
        self._input_thread.start()
        # self._busy_thread = threading.Thread(target=self._busy_worker,
        #                                      name="Busy")
        # self._busy_thread.start()

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
            # with self._busy_cv:
            #     self._busy_cv.wait()
            packet = self._input_queue.get()
            if packet is None:
                break
            self._send(packet)
            self._input_queue.task_done()

    def _send(self, packet):
        print("Sending packet: '", packet, "'")
        self._sending = True
        time.sleep(0.2)

    # def _busy_worker(self):
    #     while True:
    #         with self._sending_cv:
    #             self._sending_cv.wait_for(self._sending)
    #             # Emulate sending
    #             time.sleep(0.1)
    #             # Notify waiter.
    #             with self._busy_cv:
    #                 self._busy_cv.notify()

def my_callback():
    print("my_callback")



##### START HERE ####
print("Tests started")
my_class = ThreadTest()
my_class.register_callback(my_callback)
my_class.start()
for i in range(0, 5):
    text = "This is a long message that will be sent to test how the data is broken up into a number of 32 byte packets."
    message = str(i) + ": "
    message += text
    my_class.send(message)
my_class.stop()
print("Tests finished.")
