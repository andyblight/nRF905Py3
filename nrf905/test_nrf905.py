#!/usr/bin/env python3

import unittest

from nrf905.nrf905 import Nrf905, StateError


def callback(data):
    """ Prints out the contents of the data received. """
    print("callback", data)
    print()


class TestNrf905(unittest.TestCase):
    def setUp(self):
        self.transceiver = Nrf905()

    def tearDown(self):
        self.transceiver.close()

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

    def test_frequency(self):
        """ Test the setter and getter. """
        # Verify default.
        expected_mhz = 0.0
        default_mhz = self.transceiver.frequency_mhz
        self.assertEqual(expected_mhz, default_mhz)
        # Check that set and get works with a valid frequency.
        expected_mhz = 434.2
        self.transceiver.frequency_mhz = expected_mhz
        result_mhz = self.transceiver.frequency_mhz
        self.assertEqual(expected_mhz, expected_mhz)
        # Check that set fails with invalid frequencies.
        expected_mhz = 0
        with self.assertRaises(ValueError):
            self.transceiver.frequency_mhz = expected_mhz
        expected_mhz = 430
        with self.assertRaises(ValueError):
            self.transceiver.frequency_mhz = expected_mhz
        expected_mhz = 1000
        with self.assertRaises(ValueError):
            self.transceiver.frequency_mhz = expected_mhz

    def test_receive_address(self):
        """ Test the setter and getter. """
        # Verify default.
        expected = -1
        result = self.transceiver.receive_address
        self.assertEqual(expected, result)
        # Check that set and get works with a valid address.
        expected = 0x47474747
        self.transceiver.receive_address = expected
        result = self.transceiver.receive_address
        self.assertEqual(expected, result)
        # Check that set fails with invalid addresses.
        expected = 0x4
        self.transceiver.receive_address = expected
        result = self.transceiver.receive_address
        self.assertEqual(expected, result)
        expected = 0x123456789
        self.transceiver.receive_address = expected
        result = self.transceiver.receive_address
        self.assertEqual(expected, result)

    def test_send(self):
        """ Verify send before open fails.
        Verify write after open succeeds.
        """
        data_bytes = [20] * 32
        # StateError if write before open
        with self.assertRaises(StateError):
            self.transceiver.send(data_bytes)
        # No assert after opening.
        self.transceiver.open()
        self.transceiver.send(data_bytes)


if __name__ == "__main__":
    unittest.main()
