#!/usr/bin/env python3

import pigpio
import queue
import sys
import time
import unittest

from nrf905.nrf905gpio import nrf905gpio

# Queue instance for the callback to post to.  10 slots should be plenty for testing.
# The queue is important as it allows the callback to communicate with the test thread.
callback_queue = queue.Queue(10)

# The callback function must have this template to work.
def callback_function(num, level, tick):
    item = (num, level, tick)
    callback_queue.put(item)
    # print("callback queue size ", callback_queue.qsize())


class Testnrf905gpio(unittest.TestCase):

    def setUp(self):
        self.__pi = pigpio.pi()
        self.__gpio = nrf905gpio(self.__pi)

    def tearDown(self):
        self.__pi.stop()

    def test_init(self):
        """__init__ already called so verify GPIO pins are in correct state.
        """
        # Output pins
        for pin in nrf905gpio.output_pins:
            mode = self.__pi.get_mode(pin)
            self.assertEqual(mode, pigpio.OUTPUT)
            state = self.__pi.read(pin)
            self.assertEqual(state, 0)
        # Input pins. Mode = input, state = 1 for the callback pins.
        for pin in nrf905gpio.callback_pins:
            pin = nrf905gpio.DATA_READY
            mode = self.__pi.get_mode(pin)
            self.assertEqual(mode, pigpio.INPUT)
            state = self.__pi.read(pin)
            self.assertEqual(state, 1)

    def test_term(self):
        """__init__ already called so verify GPIO pins restored to default state.
        The state of the pins should all be 0 if nothing is connected.
        """
        self.__gpio.term(self.__pi)
        all_pins = nrf905gpio.input_pins + nrf905gpio.output_pins
        for pin in all_pins:
            mode = self.__pi.get_mode(pin)
            self.assertEqual(mode, pigpio.INPUT)
            state = self.__pi.read(pin)
            self.assertEqual(state, 0)

    def test_reset_pin(self):
        """ Test all pin values, 0-27.  All pins should be inputs.
        Pins 0-8 should be set high, pins 9-27 should be set low.
        """
        for pin in range(0, 27):
            self.__gpio.reset_pin(self.__pi, pin)
            mode = self.__pi.get_mode(pin)
            self.assertEqual(mode, pigpio.INPUT)
            state = self.__pi.read(pin)
            if pin <= 8:
                self.assertEqual(state, 1)
            else:
                self.assertEqual(state, 0)

    def test_mode_power_down(self):
        """ Verify that all output pins are set correctly. """
        self.__gpio.set_mode_power_down(self.__pi)
        expected = [0, 0, 0]
        for index, pin in enumerate(nrf905gpio.output_pins):
            state = self.__pi.read(pin)
            self.assertEqual(state, expected[index])

    def test_mode_standby(self):
        """ Verify that all output pins are set correctly. """
        self.__gpio.set_mode_power_down(self.__pi)
        expected = [1, 0, 0]
        for index, pin in enumerate(nrf905gpio.output_pins):
            state = self.__pi.read(pin)
            self.assertEqual(state, expected[index])

    def test_mode_receive(self):
        """ Verify that all output pins are set correctly. """
        self.__gpio.set_mode_power_down(self.__pi)
        expected = [1, 1, 0]
        for index, pin in enumerate(nrf905gpio.output_pins):
            state = self.__pi.read(pin)
            self.assertEqual(state, expected[index])

    def test_mode_transmit(self):
        """ Verify that all output pins are set correctly. """
        self.__gpio.set_mode_power_down(self.__pi)
        expected = [1, 1, 1]
        for index, pin in enumerate(nrf905gpio.output_pins):
            state = self.__pi.read(pin)
            self.assertEqual(state, expected[index])

    def test_set_callback(self):
        """ Create a callback and then verify that the callback function is
        called when an edge is detected.
        """
        # Setup callback
        self.__gpio.set_callback(self.__pi, nrf905gpio.DATA_READY, callback_function)
        # Force DR low then high to trigger callbacks.
        self.__pi.set_pull_up_down(nrf905gpio.DATA_READY, pigpio.PUD_DOWN)
        self.__pi.set_pull_up_down(nrf905gpio.DATA_READY, pigpio.PUD_UP)
        # Wait for the queue to have an item
        test_pass = False
        while not test_pass:
            item = callback_queue.get()
            # Check callback level = 1 (simulate DR being asserted).
            if item[1] == 1:
                self.assertEqual(item[0], nrf905gpio.DATA_READY)
                self.assertEqual(item[1], 1)
                test_pass = True
        # Restore the pin to normal
        self.__pi.set_pull_up_down(nrf905gpio.DATA_READY, pigpio.PUD_OFF)

    def test_clear_callback(self):
        # Setup callback
        self.__gpio.set_callback(self.__pi, nrf905gpio.ADDRESS_MATCHED, callback_function)
        # Clear non-existent callback - should cause exception.
        with self.assertRaises(ValueError):
            self.__gpio.clear_callback(self.__pi, nrf905gpio.CARRIER_DETECT)
        # Clear existing callback.
        self.__gpio.clear_callback(self.__pi, nrf905gpio.ADDRESS_MATCHED)
    

if __name__ == '__main__':
    unittest.main()
