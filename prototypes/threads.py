#!/usr/bin/env python3

""" This file was created so that I could test queues, threads and callacks.

TODO
Re-assemble packets of received data and print.

"""

import queue
import signal
import sys
import time
import threading


class ThreadTest:

    def __init__(self):
        self._input_queue = queue.Queue(100)
        self._input_thread = None
        self._callback_fn = None
        self._busy_semaphore = threading.Semaphore()  # Count of 1.
        self._run_thread = False

    def register_callback(self, callback_fn):
        self._callback_fn = callback_fn

    def start(self):
        self._run_thread = True
        self._input_thread = threading.Thread(target=self._input_worker,
                                              name="Input")
        self._input_thread.start()
        self._busy_thread = threading.Thread(target=self._busy_worker,
                                             name="Busy")
        self._busy_thread.start()

    def send(self, message):
        while message:  # Contains something.
            # Send first 32 bytes in a packet.
            packet = message[0:32]
            print("Posting packet: '", packet, "'")
            self._input_queue.put(packet)
            # Take the first 32 bytes off the message.
            message = message[32:]

    def stop(self):
        print("stop: called")
        self._run_thread = False
        # join threads
        self._input_thread.join()
        self._busy_thread.join()
        sys.exit(1)

    def _input_worker(self):
        print("_input_worker: started.")
        while self._run_thread:
            packet = self._input_queue.get()
            if packet is not None:
                self._send(packet)
                self._input_queue.task_done()
        print("_input_worker: exit. p:", packet, ", rt:", self._run_thread)

    def _send(self, packet):
        print("Sending packet: '", packet, "'")
        # Wait for transceiver to be free.
        self._busy_semaphore.acquire()
        # Not busy so send
        print("Sending packet: written.")
        self._sending = True

    def _busy_worker(self):
        # Fakes the DR callback.
        print("_busy_worker: started.")
        while self._run_thread:
            # Emulate being busy
            time.sleep(0.2)
            if self._sending:
                # Wait for DR callback after send. Fake this by waiting for 0.1
                time.sleep(0.1)
                print("_busy_worker: DR callback.")
                self._sending = False
                # When callback happens, release semaphore.
                self._busy_semaphore.release()
            else:
                print("_busy_worker: Not sending.")
        print("_busy_worker: exit. rt:", self._run_thread)

def my_callback():
    print("my_callback")


class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


def service_shutdown(signum, frame):
    print('Caught signal %d' % signum)
    raise ServiceExit


##### START HERE ####
# Register the signal handlers
signal.signal(signal.SIGTERM, service_shutdown)
signal.signal(signal.SIGINT, service_shutdown)
print("Tests started")
try:
    my_class = ThreadTest()
    my_class.register_callback(my_callback)
    my_class.start()
    for i in range(0, 5):
        text = "This is a long message that will be sent to test how the data is broken up into a number of 32 byte packets."
        message = str(i) + ": "
        message += text
        my_class.send(message)
    time.sleep(100)
except ServiceExit:
    pass

my_class.stop()

print("Tests finished.")
