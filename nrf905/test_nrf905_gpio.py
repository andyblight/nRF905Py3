#!/usr/bin/env python3

import pigpio
import queue
import sys
import time
import unittest

from nrf905.nrf905_gpio import Nrf905Gpio

# Queue instance for the callback to post to.  10 slots should be plenty for testing.
# The queue is important as it allows the callback to communicate with the test thread.
callback_queue = queue.Queue(10)

# The callback function must have this template to work.
def callback_function(num, level, tick):
    item = (num, level, tick)
    callback_queue.put(item)
    # print("callback queue size ", callback_queue.qsize())


class TestNrf905Gpio(unittest.TestCase):

    def setUp(self):
        self.__pi = pigpio.pi()
        self.__gpio = Nrf905Gpio(self.__pi)

    def tearDown(self):
        self.__pi.stop()

    def test_init(self):
        """__init__ already called so verify GPIO output pins are in correct
        state.  The callback pins are left as default.
        """
        for pin in Nrf905Gpio.output_pins:
            mode = self.__pi.get_mode(pin)
            self.assertEqual(mode, pigpio.OUTPUT)
            state = self.__pi.read(pin)
            self.assertEqual(state, 0)

    def check_output_pins(self, expected):
        """ The state of each output pin is tested against 'expected'.
        'expected' is a list that contains the expected state of the output pins
        in this order:
            POWER_UP
            TRANSMIT_RECEIVE_CHIP_ENABLE
            TRANSMIT_ENABLE
        This is done outside a loop so that the pin that fails can be identified
        in the text output.
        """
        self.assertEqual(self.__pi.read(Nrf905Gpio.POWER_UP), expected[0])
        self.assertEqual(self.__pi.read(Nrf905Gpio.TRANSMIT_RECEIVE_CHIP_ENABLE), expected[1])
        self.assertEqual(self.__pi.read(Nrf905Gpio.TRANSMIT_ENABLE), expected[2])

    def check_callback_pins(self):
        """ The state of each callback pin is tested.
        Each pin should be an input pin and have a state of 0.  The pins are:
            DATA_READY
            CARRIER_DETECT
            ADDRESS_MATCHED
        This is done outside a loop so that the pin that fails can be identified
        in the text output.
        """
        pin = Nrf905Gpio.DATA_READY
        mode = self.__pi.get_mode(pin)
        self.assertEqual(mode, pigpio.INPUT)
        self.assertEqual(self.__pi.read(pin), 0)
        pin = Nrf905Gpio.CARRIER_DETECT
        mode = self.__pi.get_mode(pin)
        self.assertEqual(mode, pigpio.INPUT)
        self.assertEqual(self.__pi.read(pin), 0)
        pin = Nrf905Gpio.ADDRESS_MATCHED
        mode = self.__pi.get_mode(pin)
        self.assertEqual(mode, pigpio.INPUT)
        self.assertEqual(self.__pi.read(pin), 0)

    def test_term(self):
        """ All pins should be in input mode with state = 0.
        """
        self.__gpio.term(self.__pi)
        self.check_output_pins([0, 0, 0])
        self.check_callback_pins()

    def test_reset_pin(self):
        """ Test all usable GPIO pins.  All pins should be inputs.
        Pins 0-8 should be set high, pins 9-27 should be set low.
        Note: Some pins are not usable by pigpio so a list of pins is used.
        When you try to use a pin that is not allowed, you get the message
        "pigpio.error: 'no permission to update GPIO'".
        TODO The GPIOs are only for the RPi 1A/B.  Fix so that the tests are
        extended for RPi 1B+ and later.
        """
        pins_to_reset = [2, 3, 4, 7, 8, 9, 10, 11, 14, 15, 17, 18, 22, 23, 24, 25, 27]
        # This is the full list of pins on the RPi B+ but this causes a failure on the 1B.
        # pins_to_reset = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
        for pin in pins_to_reset:
            self.__gpio.reset_pin(self.__pi, pin)
            mode = self.__pi.get_mode(pin)
            self.assertEqual(mode, pigpio.INPUT)
            state = self.__pi.read(pin)
            if pin <= 8:
                self.assertEqual(state, 1)
            else:
                self.assertEqual(state, 0)

    def test_output_pins(self):
        """ Verify that all output pins are set correctly. """
        self.check_output_pins([0, 0, 0])
        # Check standby 
        self.__gpio.set_mode_standby(self.__pi)
        self.check_output_pins([1, 0, 0])
        # Check power down
        self.__gpio.set_mode_power_down(self.__pi)
        self.check_output_pins([0, 0, 0])
        # Set receive
        self.__gpio.set_mode_receive(self.__pi)
        self.check_output_pins([1, 1, 0])
        # Set transmit
        self.__gpio.set_mode_transmit(self.__pi)
        self.check_output_pins([1, 1, 1])

    def test_set_callback(self):
        """ Create a callback and then verify that the callback function is
        called when an edge is detected.
        """
        # Setup callback
        self.__gpio.set_callback(self.__pi, Nrf905Gpio.DATA_READY, callback_function)
        # Force DR low then high to trigger callbacks.
        self.__pi.set_pull_up_down(Nrf905Gpio.DATA_READY, pigpio.PUD_DOWN)
        self.__pi.set_pull_up_down(Nrf905Gpio.DATA_READY, pigpio.PUD_UP)
        # Wait for the queue to have an item
        test_pass = False
        while not test_pass:
            item = callback_queue.get()
            # Check callback level = 1 (simulate DR being asserted).
            if item[1] == 1:
                self.assertEqual(item[0], Nrf905Gpio.DATA_READY)
                self.assertEqual(item[1], 1)
                test_pass = True
        # Restore the pin to normal
        self.__pi.set_pull_up_down(Nrf905Gpio.DATA_READY, pigpio.PUD_OFF)

    def test_clear_callback(self):
        # Setup callback
        self.__gpio.set_callback(self.__pi, Nrf905Gpio.ADDRESS_MATCHED, callback_function)
        # Clear non-existent callback - should return False.
        result = self.__gpio.clear_callback(self.__pi, Nrf905Gpio.CARRIER_DETECT)
        self.assertFalse(result)
        # Clear existing callback - should return True.
        result = self.__gpio.clear_callback(self.__pi, Nrf905Gpio.ADDRESS_MATCHED)
        self.assertTrue(result)
    

if __name__ == '__main__':
    unittest.main()
