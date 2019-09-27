#!/usr/bin/env python3

import pigpio
import unittest
import sys

from nrf905.nrf905_spi import Nrf905Spi
from nrf905.nrf905_config import Nrf905ConfigRegister


def callback(data):
    """ Prints out the contents of the data received. """
    print("callback", data)
    print()


class TestNrf905Spi(unittest.TestCase):

    def setUp(self):
        self.pi = pigpio.pi()
        print("setUp: self.pi:", self.pi)
        self.spi = Nrf905Spi()
        print("setUp: self.spi:", self.spi)
        self.spi.open(self.pi)

    def tearDown(self):
        print("tearDown: self.spi:", self.spi)
        self.spi.close()
        print("tearDown: self.pi:", self.pi)
        self.pi.stop()

    def test_configuration_register_read_write(self):
        """ Verify that the defaults can be read.
        Verify that certain values can be modified.
        """
        # Test defaults
        print("tcrrw: self.spi:", self.spi)
        # Check that we can read 10 bytes
        config_register = self.spi.configuration_register_read()
        data_bytes = config_register.get_all()
        self.assertEqual(len(data_bytes), 10)
        config_register.print()
        # Set registers to power on defaults
        check_register = Nrf905ConfigRegister()
        self.spi.configuration_register_write(check_register)
        # Read back and verify that defaults are correct
        config_register = self.spi.configuration_register_read()
        self.assertTrue(config_register == check_register)
        # Verify board defaults
        check_register.board_defaults()
        self.spi.configuration_register_write(check_register)
        config_register = self.spi.configuration_register_read()
        self.assertTrue(config_register == check_register)
        # Modify RX address
        new_address = 0x012345678
        check_register.set_rx_address(new_address)
        config_register.set_rx_address(new_address)
        # Write, read back and verify that they are equal
        self.spi.configuration_register_write(config_register)
        config_register = self.spi.configuration_register_read()
        self.assertTrue(config_register == check_register)

    def test_channel_config(self):
        # Set config register to known state
        check_register = Nrf905ConfigRegister()
        self.spi.configuration_register_write(check_register)
        config_register = self.spi.configuration_register_read()
        self.assertTrue(config_register == check_register)
        # Tests that should work
        passing_tests = [
            (0,     False, 0), (0x1FF, False, 1),
            (0xFF,  True,  2), (15,    True,  3)
        ]
        for test in passing_tests:
            # Write to device
            print("tcc:", test[0], test[1], test[2])
            self.spi.channel_config(test[0], test[1], test[2])
            # Update check_register with same data
            check_register.set_channel_number(test[0])
            check_register.set_hfreq_pll(test[1])
            check_register.set_pa_pwr(test[2])
            # Read back and verify expected data matches
            config_register = self.spi.configuration_register_read()
            config_register.print()
            self.assertTrue(config_register == check_register)
        # Tests that should fail
        value_errors = [
            (-1,    False, 0), (0,     False, -1),
            (0x200, False, 1), (0x200, False, -12)
        ]
        for test in value_errors:
            # Attempt writing to device.
            with self.assertRaises(ValueError):
                self.spi.channel_config(test[0], test[1], test[2])

#        # Modify values.
#        frequency_mhz = 433.2
#        rx_address = 0xABABABAB
#        crc_bits = 8
#        config_register = self.spi.configuration_register_create(frequency_mhz, rx_address, crc_bits)
#        self.spi.configuration_register_write(self.pi, config_register)
#        # Verify changes have been written. 
#        data = self.spi.configuration_register_read(self.pi)
#        self.assertEqual(len(data), 10)
#        self.spi.configuration_register_print(data)

#    def test_transmit_address_read_write(self):
#        """ Verify that the functions that write to and read from the TX_ADDRESS
#        register work as expected. """
#        # Verify that default value, E7E7E7E7, can be read.
#        address = self.spi.read_transmit_address(self.pi)
#        expected_address = 0xE7E7E7E7
#        print("Expected address", expected_address, "actual address", address)
#        # self.assertEqual(address, expected_address)
#        self.assertEqual(0, self.spi.get_status_register())


if __name__ == '__main__':
    unittest.main()
