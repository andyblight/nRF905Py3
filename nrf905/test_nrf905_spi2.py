#!/usr/bin/env python3

import pigpio
import unittest
import sys

# from nrf905.nrf905_spi import Nrf905Spi


def callback(data):
    """ Prints out the contents of the data received. """
    print("callback", data)
    print()


class Nrf905Spi:

    def __init__(self):
        self.__spi_h = None
        self.__status = 0

    def open(self, pi):
        print("open:", pi)
        self.__pi = pi
        print("open self.__pi:", self.__pi)
        self.__spi_h = self.__pi.spi_open(0, 32000, 2)
        print("open self.__spi_h:", self.__spi_h)

    def close(self):
        print("close: self.__pi:", self.__pi)
        self.__pi.spi_close(self.__spi_h)

    def default_config_register(self):
        register = bytearray(9)
        register[-1] = 0b01101100
        register[0] = 0
        register[1] = 0b01000100
        register[2] = 0b00100000
        register[3] = 0b00100000
        register[4] = 0xE7
        register[5] = 0xE7
        register[6] = 0xE7
        register[7] = 0xE7
        register[8] = 0b11100111
        return register

    def command_read_config(self):
        # Command to read all 10 bytes
        read_config_command = bytearray(11)
        read_config_command[0] = 0b00100000
        result = self.send_command(read_config_command)
        print("default register", self.default_config_register().hex())
        return result

    def send_command(self, b_command):
        print("Command is 0x", b_command.hex())
        # Transfer the data
        print("send_command: self.__pi:", self.__pi)
        print("send_command self.__spi_h:", self.__spi_h)
        (count, data) = self.__pi.spi_xfer(self.__spi_h, b_command)
        # Print what we received
        print("Received", count, data)
        if count > 0:
            self.__status = data.pop(0)
            print("Status 0x", self.__status)
            print("Data bytes", len(data), "0x", data.hex())
        return data


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
        self.spi.command_read_config()

    def test_the_old_way(self):
        spi_h = self.pi.spi_open(0, 32000, 2)
        print("ttow: spi_h:", spi_h)
        read_config_command = bytearray(11)
        read_config_command[0] = 0b00100000
        (count, data) = self.pi.spi_xfer(spi_h, read_config_command)
        # Print what we received
        print("Received", count, data)
        if count > 0:
            status = data.pop(0)
            print("Status 0x", status)
            print("Data bytes", len(data), "0x", data.hex())
        print("ttow: spi_h:", spi_h)
        self.pi.spi_close(spi_h)

#        data = self.spi.configuration_register_read(self.pi)
#        self.assertEqual(len(data), 10)
#        self.spi.configuration_register_print(data)
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
