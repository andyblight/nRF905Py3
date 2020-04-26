#!/usr/bin/env python3

import time
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
        time.sleep(0.001)
        self.transceiver.close()

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
        # Check that set fails with an invalid address.
        expected = 0x123456789
        with self.assertRaises(StateError):
            self.transceiver.receive_address = expected

    def test_send(self):
        """ Verify send before open fails.
        Verify write after open succeeds.
        """
        data_bytes = [20] * 32
        # StateError if write before open
        with self.assertRaises(StateError):
            self.transceiver.send(data_bytes)
        # No assert after opening.
        self.transceiver.receive_address = 0x43454749
        self.transceiver.transmit_address = 0x4345474A
        self.transceiver.open()
        self.transceiver.send(data_bytes)


if __name__ == "__main__":
    unittest.main()
