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
        self._busy_semaphore = threading.Semaphore()  # Count of 1.

    def register_callback(self, callback_fn):
        self._callback_fn = callback_fn

    def start(self):
        self._input_thread = threading.Thread(target=self._input_worker,
                                              name="Input")
        self._input_thread.start()
        self._busy_thread = threading.Thread(target=self._busy_worker,
                                             name="Busy")
        self._busy_thread.start()

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
        # TODO add ctrl+c handling.
        while True:
            packet = self._input_queue.get()
            if packet is not None:
                self._send(packet)
            self._input_queue.task_done()

    def _send(self, packet):
        print("Sending packet: '", packet, "'")
        # Wait for transceiver to be free.
        self._busy_semaphore.acquire()
        # Not busy so send
        print("Sending packet: written.")
        self._sending = True

    def _busy_worker(self):
        # This attempts to fake the DR callback.
        while True:
            # Emulate being busy
            time.sleep(0.2)
            if self._sending:
                # Wait for DR callback after send. Fake this by waiting for 0.1
                time.sleep(0.1)
                print("_busy_worker: DR callback.")
                self._sending = False
                # When callback happens, release semaphore.
                self._busy_semaphore.release()

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
