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
        self.spi = nrf905spi(self.pi)

    def tearDown(self):
        self.spi.close(self.pi)
        self.pi.stop()

    def test_configuration_register_create(self):
        """ Tests various aspects of the create function """
        # Test frequency values
        frequency_mhz = 433.2
        rx_address = 0xDDCCBBAA
        crc_mode = 16
        data = self.spi.configuration_register_create(frequency_mhz, rx_address, crc_mode)
        self.assertEqual(data[0], 0b01101100)
        self.assertEqual(data[1], 0b00)
        self.assertEqual(data[2], 0)
        self.assertEqual(data[3], 0)
        self.assertEqual(data[4], 0)
        self.assertEqual(data[5], 0xAA)
        self.assertEqual(data[6], 0xBB)
        self.assertEqual(data[7], 0xCC)
        self.assertEqual(data[8], 0xDD)
        self.assertEqual(data[9], 0b11000000)
        # Frequency not found.
        frequency_mhz = 512.7
        with self.assertRaises(ValueError):
            data = self.spi.configuration_register_create(frequency_mhz, rx_address, crc_mode)

    def test_create_print(self):
        frequency_mhz = 433.7
        rx_address = 0xDDCCBBAA
        crc_mode = 0
        data = self.spi.configuration_register_create(frequency_mhz, rx_address, crc_mode)
        self.spi.configuration_register_print(data)

    def test_configuration_register_read(self):
        data = self.spi.configuration_register_read(self.pi)
        self.assertEqual(len(data), 10)
        self.spi.configuration_register_print(data)
        



if __name__ == '__main__':
    unittest.main()
