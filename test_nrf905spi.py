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

    def test_create_print(self):
        pi = pigpio.pi()
        spi = nrf905spi(pi)
        frequency_mhz = 434.7
        rx_address = 0xDDCCBBAA
        crc_mode = 0
        data = spi.configuration_register_create(frequency_mhz, rx_address, crc_mode)
        spi.configuration_register_print(data)
        spi.close(pi)
        pi.stop()


if __name__ == '__main__':
    unittest.main()
