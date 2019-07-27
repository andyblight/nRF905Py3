#!/usr/bin/env python3

import unittest
import sys

from nrf905.nrf905 import nrf905, StateError


def callback(data):
    """ Prints out the contents of the data received. """
    print("callback", data)
    print()


class Testnrf905(unittest.TestCase):

    def test_open_rx_rx(self):
        # No exceptions expected
        transceiver = nrf905()
        transceiver.open(434, callback)
        transceiver.open(434, callback)
        transceiver.close()

    def test_open_tx_rx(self):
        # Expect exception on second call
        transceiver = nrf905()
        transceiver.open(434)
        with self.assertRaises(StateError):
            transceiver.open(434, callback)
        transceiver.close()

    def test_open_rx_tx(self):
        # Expect exception on second call
        transceiver = nrf905()
        transceiver.open(434, callback)
        with self.assertRaises(StateError):
            transceiver.open(434)
        transceiver.close()

    def test_open_tx_tx(self):
        # No exceptions expected
        transceiver = nrf905()
        transceiver.open(434)
        transceiver.open(434)
        transceiver.close()

    def test_write(self):
        transceiver = nrf905()
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
        transceiver = nrf905()
        transceiver.open(434, callback)
        transceiver.close()

    def test_set_pins(self):
        transceiver = nrf905()
        pins = [11, 12, 13, 14, 15]
        # No exception before open.
        transceiver.set_pins(pins)
        # StateError after opening.
        transceiver.open(434)
        with self.assertRaises(StateError):
            transceiver.set_pins(pins)
        transceiver.close()

    def test_set_spi_bus(self):
        transceiver = nrf905()
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
        transceiver = nrf905()
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

if __name__ == '__main__':
    unittest.main()
