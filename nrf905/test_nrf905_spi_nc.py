#!/usr/bin/env python3

import pigpio
import unittest
import sys

from nrf905.nrf905_spi import Nrf905Spi


class TestNrf905SpiNc(unittest.TestCase):

    def setUp(self):
        self.pi = pigpio.pi()
        self.spi = Nrf905Spi(self.pi, 0)

    def tearDown(self):
        self.spi.close(self.pi)
        self.pi.stop()

    def test_configuration_register_create(self):
        """ Tests various aspects of the create function """
        # Test valid frequency values
        frequency_mhz = 433.2
        rx_address = 0xDDCCBBAA
        crc_mode = 16
        data = self.spi.configuration_register_create(frequency_mhz, rx_address, crc_mode)
        self.assertEqual(data[0], 0b01101100)
        self.assertEqual(data[1], 0b00)
        self.assertEqual(data[2], 0b01000100)
        self.assertEqual(data[3], 32)
        self.assertEqual(data[4], 32)
        self.assertEqual(data[5], 0xAA)
        self.assertEqual(data[6], 0xBB)
        self.assertEqual(data[7], 0xCC)
        self.assertEqual(data[8], 0xDD)
        self.assertEqual(data[9], 0b11011000)
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

    def test_status_register(self):
        """ Gets the last read value of the status register.  When not
        connected, this is always 0.
        """
        result = self.spi.get_status_register()
        self.assertEqual(result, 0)


if __name__ == '__main__':
    unittest.main()
