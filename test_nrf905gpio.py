#!/usr/bin/env python3

import pigpio
import unittest
import sys
from time import sleep

from nrf905.nrf905gpio import nrf905gpio

# Outside class so that callback function has correct template.
__callback_pin = -1
__callback_pin_state = -1

def callback_function(num, level, tick):
    __callback_pin = num
    __callback_pin_state = level


class Testnrf905gpio(unittest.TestCase):

    output_pins = [nrf905gpio.POWER_UP,
                   nrf905gpio.TRANSMIT_ENABLE,
                   nrf905gpio.TRANSMIT_RECEIVE_CHIP_ENABLE]

    def setUp(self):
        self.__pi = pigpio.pi()
        self.__gpio = nrf905gpio(self.__pi)

    def tearDown(self):
        self.__pi.stop()

    def test_init(self):
        """__init__ already called so verify GPIO pins are in correct state.
        """
        # Output pins
        for index, pin in enumerate(self.output_pins):
            mode = self.__pi.get_mode(pin)
            self.assertEqual(mode, pigpio.OUTPUT)
            state = self.__pi.read(pin)
            self.assertEqual(state, 0)
        # Input pins
        pin = nrf905gpio.DATA_READY
        mode = self.__pi.get_mode(pin)
        self.assertEqual(mode, pigpio.INPUT)
        state = self.__pi.read(pin)
        self.assertEqual(state, 0)

    def term(self):
        """__init__ already called so verify GPIO pins restored to default state.
        The state of the pins should all be 0 if nothing is connected.
        """
        self.__gpio.term(self.__pi)
        pins = [nrf905gpio.POWER_UP, nrf905gpio.TRANSMIT_ENABLE,
                nrf905gpio.TRANSMIT_RECEIVE_CHIP_ENABLE, nrf905gpio.DATA_READY]
        for pin in pins:
            mode = self.__pi.get_mode(pin)
            self.assertEqual(mode, pigpio.INPUT)
            state = self.__pi.read(pin)
            self.assertEqual(state, 0)

    def reset_pin(self):
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

    def mode_power_down(self):
        """ Verify that all output pins are set to 0. """
        self.__gpio.set_mode_power_down(self.__pi)
        expected = [0, 0, 0]
        for index, pin in enumerate(self.output_pins):
            state = self.__pi.read(pin)
            self.assertEqual(state, expected[i])

    def mode_standby(self):
        """ Verify that all output pins are set correctly. """
        self.__gpio.set_mode_power_down(self.__pi)
        expected = [1, 0, 0]
        for index, pin in enumerate(self.output_pins):
            state = self.__pi.read(pin)
            self.assertEqual(state, expected[i])

    def mode_receive(self):
        """ Verify that all output pins are set to 0. """
        self.__gpio.set_mode_power_down(self.__pi)
        expected = [1, 1, 0]
        for index, pin in enumerate(self.output_pins):
            state = self.__pi.read(pin)
            self.assertEqual(state, expected[i])

    def mode_transmit(self):
        """ Verify that all output pins are set to 0. """
        self.__gpio.set_mode_power_down(self.__pi)
        expected = [1, 1, 1]
        for index, pin in enumerate(self.output_pins):
            state = self.__pi.read(pin)
            self.assertEqual(state, expected[i])

    def test_callback(self):
        # Ensure callback vars are set to known invalid state.
        __callback_pin = -1
        __callback_pin_state = -1
        # Setup callback
        self.__gpio.set_data_ready_callback(self.__pi, callback_function)
        # Force DR high to trigger callback.
        self.__pi.set_pull_up_down(nrf905gpio.DATA_READY, pigpio.PUD_UP)
        # Wait for 5 ms to allow the callback to trigger.
        sleep(0.005)
        # Check that the callback variables have been set correctly
        self.assertEqual(__callback_pin, nrf905gpio.DATA_READY)
        self.assertEqual(__callback_pin_state, 1)
        # Restore the pin to normal
        self.__pi.set_pull_up_down(nrf905gpio.DATA_READY, pigpio.PUD_DOWN)
        # Clear the callback by changing mode.


if __name__ == '__main__':
    unittest.main()
