#!/usr/bin/env python3

import pigpio
import unittest
import sys

from nrf905.nrf905gpio import nrf905gpio


class Testnrf905gpio(unittest.TestCase):

    def setUp(self):
        self.pi = pigpio.pi()

    def tearDown(self):
        self.pi.stop()

    def test_init(self):
        gpio = nrf905gpio(self.pi)

    def term(self):
        gpio = nrf905gpio(self.pi)
        gpio.init(self.pi)
        gpio.term(self.pi)
        
        
    def reset_pin(self):
        # Test all pin values, 0-27.  All pins should be inputs,
        # pins 0-8 should be set high, pins 9-27 should be set low.
        gpio = nrf905gpio(self.pi)
        gpio.init(self.pi)
        # After initialisation, 
        
        
        gpio.term()


if __name__ == '__main__':
    unittest.main()
