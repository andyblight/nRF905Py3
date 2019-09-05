#!/usr/bin/env python3

import unittest
import sys

from nrf905 import Nrf905, StateError


def callback(data):
    """ Prints out the contents of the data received. """
    print("callback", data)
    print()


class TestNrf905(unittest.TestCase):

    def test_open_rx_rx(self):
        # No exceptions expected
        transceiver = Nrf905()
        transceiver.open(434, callback)
        transceiver.open(434, callback)
        transceiver.close()

    def test_open_tx_rx(self):
        # Expect exception on second call
        transceiver = Nrf905()
        transceiver.open(434)
        with self.assertRaises(StateError):
            transceiver.open(434, callback)
        transceiver.close()

    def test_open_rx_tx(self):
        # Expect exception on second call
        transceiver = Nrf905()
        transceiver.open(434, callback)
        with self.assertRaises(StateError):
            transceiver.open(434)
        transceiver.close()

    def test_open_tx_tx(self):
        # No exceptions expected
        transceiver = Nrf905()
        transceiver.open(434)
        transceiver.open(434)
        transceiver.close()

    def test_write(self):
        transceiver = Nrf905()
        data_bytes = [20] * 32
        # StateError if write before open
        with self.assertRaises(StateError):
            transceiver.write(data_bytes)
        # No assert after opening.
        transceiver.open(434)
        transceiver.write(data_bytes)
        transceiver.close()

    def test_read_success(self):
        # TODO This test needs to invoke the callback and verify what is returned.
        transceiver = Nrf905()
        transceiver.open(434, callback)
        transceiver.close()

    def test_set_pins(self):
        transceiver = Nrf905()
        pins = [11, 12, 13, 14, 15]
        # No exception before open.
        transceiver.set_pins(pins)
        # StateError after opening.
        transceiver.open(434)
        with self.assertRaises(StateError):
            transceiver.set_pins(pins)
        transceiver.close()

    def test_set_spi_bus(self):
        transceiver = Nrf905()
        # Verify it works before open for 0 and 1 only.
        bus = 0
        transceiver.set_spi_bus(bus)
        bus = 1
        transceiver.set_spi_bus(bus)
        bus = -1
        with self.assertRaises(ValueError):
           transceiver.set_spi_bus(bus)
        bus = 3
        with self.assertRaises(ValueError):
           transceiver.set_spi_bus(bus)
        # Set after open causes StateError.
        transceiver.open(434)
        bus = 0
        with self.assertRaises(StateError):
           transceiver.set_spi_bus(bus)
        transceiver.close()

    def test_set_address(self):
        transceiver = Nrf905()
        # Verify it works before open for unsigned 32 bit integers.
        address = 0
        transceiver.set_address(address)
        address = 0xffffffff
        transceiver.set_address(address)
        # Verify values that are not unsigned 32 bit integers generate exceptions.
        address = -1
        with self.assertRaises(ValueError):
            transceiver.set_address(address)
        address = 3.4
        with self.assertRaises(TypeError):
            transceiver.set_address(address)
        # Set after open asserts with StateError.
        transceiver.open(434)
        address = 105
        with self.assertRaises(StateError):
            transceiver.set_address(address)
        transceiver.close()

    def test_set_crc_mode(self):
        transceiver = Nrf905()
        # Verify it works before open for 0, 8 and 16.
        crc_mode = 0
        transceiver.set_crc_mode(crc_mode)
        crc_mode = 8
        transceiver.set_crc_mode(crc_mode)
        crc_mode = 16
        transceiver.set_crc_mode(crc_mode)
        # Verify ValueError before open for not 0, 8 and 16.
        crc_mode = -1
        with self.assertRaises(ValueError):
            transceiver.set_crc_mode(crc_mode)
        crc_mode = 1
        with self.assertRaises(ValueError):
            transceiver.set_crc_mode(crc_mode)
        crc_mode = 7
        with self.assertRaises(ValueError):
            transceiver.set_crc_mode(crc_mode)
        crc_mode = 9
        with self.assertRaises(ValueError):
            transceiver.set_crc_mode(crc_mode)
        crc_mode = 15
        with self.assertRaises(ValueError):
            transceiver.set_crc_mode(crc_mode)
        crc_mode = 17
        with self.assertRaises(ValueError):
            transceiver.set_crc_mode(crc_mode)
        crc_mode = 200
        with self.assertRaises(ValueError):
            transceiver.set_crc_mode(crc_mode)
        # Set after open causes StateError.
        transceiver.open(434)
        crc_mode = 8
        with self.assertRaises(StateError):
            transceiver.set_crc_mode(crc_mode)
        transceiver.close()

if __name__ == '__main__':
    unittest.main()
