#!/usr/bin/env python3

import pigpio
import unittest
import sys

from nrf905.nrf905spi import nrf905spi


def callback(data):
    """ Prints out the contents of the data received. """
    print("callback", data)
    print()


class Testnrf905spi(unittest.TestCase):

    def setUp(self):
        self.pi = pigpio.pi()
        self.spi = nrf905spi(pi)

    def tearDown(self):
        self.spi.close(self.pi)
        self.pi.stop()

    def test_frequency_to_bits(self):
        """ Only need to test for match in list and not found """
        # Frequency found
        frequency = 433.2
        result = self.spi.__frequency_to_bits(frequency)
        self.assertEqual(result[0], 0b01101100)
        self.assertEqual(result[1], 0b00)
        # Frequency not found.
        frequency = 512.7
        with self.assertRaises(ValueError):
            result = self.spi.__frequency_to_bits(frequency)

    def test_create_print(self):
        frequency_mhz = 433.7
        rx_address = 0xDDCCBBAA
        crc_mode = 0
        data = self.spi.configuration_register_create(frequency_mhz, rx_address, crc_mode)
        self.spi.configuration_register_print(data)

if __name__ == '__main__':
    unittest.main()
