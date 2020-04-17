#!/usr/bin/env python3

import unittest

from nrf905.nrf905 import Nrf905, StateError


def callback(data):
    """ Prints out the contents of the data received. """
    print("callback", data)
    print()


class TestNrf905(unittest.TestCase):
    def setUp(self):
        self.self.transceiver = Nrf905()

    def tearDown(self):
        self.transceiver.close()

    def test_frequency(self):
        """ Test the setter. """

    def test_write(self):
        """ Verify write before open fails.
        Verify write after open succeeds.
        """
        data_bytes = [20] * 32
        # StateError if write before open
        with self.assertRaises(StateError):
            self.transceiver.write(data_bytes)
        # No assert after opening.
        self.transceiver.open(callback)
        self.transceiver.write(data_bytes)

    # THE FOLLOWING TESTS ARE BROKEN
    def test_set_address(self):
        # Verify it works before open for unsigned 32 bit integers.
        address = 0
        self.transceiver.set_address(address)
        address = 0xFFFFFFFF
        self.transceiver.set_address(address)
        # Verify values that are not unsigned 32 bit integers generate
        # exceptions.
        address = -1
        with self.assertRaises(ValueError):
            self.transceiver.set_address(address)
        address = 3.4
        with self.assertRaises(TypeError):
            self.transceiver.set_address(address)
        # Set after open asserts with StateError.
        self.transceiver.open(434)
        address = 105
        with self.assertRaises(StateError):
            self.transceiver.set_address(address)

    def test_open_rx_rx(self):
        # No exceptions expected
        self.transceiver.open(434, callback)
        self.transceiver.open(434, callback)

    def test_open_tx_rx(self):
        # Expect exception on second call
        self.transceiver.open(434)
        with self.assertRaises(StateError):
            self.transceiver.open(434, callback)
        self.transceiver.close()

    def test_open_rx_tx(self):
        # Expect exception on second call
        self.transceiver.open(434, callback)
        with self.assertRaises(StateError):
            self.transceiver.open(434)
        self.transceiver.close()

    def test_open_tx_tx(self):
        # No exceptions expected
        self.transceiver.open(434)
        self.transceiver.open(434)
        self.transceiver.close()

    def test_read_success(self):
        self.transceiver.open(434, callback)
        # TODO This test needs to invoke the callback and verify what is
        # returned.
        self.transceiver.close()

    def test_set_crc_mode(self):
        # Verify it works before open for 0, 8 and 16.
        crc_mode = 0
        self.transceiver.set_crc_mode(crc_mode)
        crc_mode = 8
        self.transceiver.set_crc_mode(crc_mode)
        crc_mode = 16
        self.transceiver.set_crc_mode(crc_mode)
        # Verify ValueError before open for not 0, 8 and 16.
        crc_mode = -1
        with self.assertRaises(ValueError):
            self.transceiver.set_crc_mode(crc_mode)
        crc_mode = 1
        with self.assertRaises(ValueError):
            self.transceiver.set_crc_mode(crc_mode)
        crc_mode = 7
        with self.assertRaises(ValueError):
            self.transceiver.set_crc_mode(crc_mode)
        crc_mode = 9
        with self.assertRaises(ValueError):
            self.transceiver.set_crc_mode(crc_mode)
        crc_mode = 15
        with self.assertRaises(ValueError):
            self.transceiver.set_crc_mode(crc_mode)
        crc_mode = 17
        with self.assertRaises(ValueError):
            self.transceiver.set_crc_mode(crc_mode)
        crc_mode = 200
        with self.assertRaises(ValueError):
            self.transceiver.set_crc_mode(crc_mode)
        # Set after open causes StateError.
        self.transceiver.open(434)
        crc_mode = 8
        with self.assertRaises(StateError):
            self.transceiver.set_crc_mode(crc_mode)
        self.transceiver.close()


if __name__ == "__main__":
    unittest.main()
