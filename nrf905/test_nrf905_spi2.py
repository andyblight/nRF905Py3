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
        config_register = self.spi.configuration_register_read()
        data_bytes = config_register.get_all()
        self.assertEqual(len(data_bytes), 10)
        print("Status 0x", self.spi.status_register_get())
        config_register.print()

        # # Test channel_config()
        # self.spi.channel_config(0, False, 0)
        # print("Expected command: 0x8000")
        # self.spi.channel_config(15, True, 3)
        # print("Expected command: 0x8E0F")
        # self.spi.channel_config(0x1FF, False, 1)
        # print("Expected command: 0x85FF")
        # # Check that values were actually written.
        # config_register = self.spi.configuration_register_read()
        # self.assertEqual(len(config_register), 10)
        # print("Status 0x", self.spi.status_register_get())
        # print("Data bytes", len(config_register), "0x", config_register.hex())
        # print("default register", self.spi.configuration_register_default().hex())
        # self.spi.configuration_register_print(config_register)

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
