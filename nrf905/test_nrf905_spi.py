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
        # print("setUp: self.pi:", self.pi)
        self.spi = Nrf905Spi()
        # print("setUp: self.spi:", self.spi)
        self.spi.open(self.pi)

    def tearDown(self):
        # print("tearDown: self.spi:", self.spi)
        self.spi.close()
        # print("tearDown: self.pi:", self.pi)
        self.pi.stop()

    def test_configuration_register_read_write(self):
        """ Verify that the defaults can be read.
        Verify that certain values can be modified.
        """
        # Test defaults
        # print("tcrrw: self.spi:", self.spi)
        # Check that we can read 10 bytes
        config_register = self.spi.configuration_register_read()
        data_bytes = config_register.get_all()
        self.assertEqual(len(data_bytes), 10)
        # config_register.print()
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

    def test_transmit_payload_read_write(self):
        """ Verify that values can be written to and read from the transmit
        payload registers.  Also verify that only the number of bytes specifed
        in the payload width registers are used.
        """
        # Set config registers to power on defaults
        check_register = Nrf905ConfigRegister()
        self.spi.configuration_register_write(check_register)
        config_register = self.spi.configuration_register_read()
        self.assertTrue(config_register == check_register)
        # Test 32 byte transfers
        payload_width = 32
        write_payload = bytearray(payload_width)
        for i in range(0, payload_width):
            write_payload[i] = i + 1
        self.spi.write_transmit_payload(write_payload)
        read_payload = self.spi.read_transmit_payload()
        for i in range(0, payload_width):
            self.assertEqual(write_payload[i], read_payload[i])
        # Test 14 byte transfers
        payload_width = 14
        check_register.set_tx_pw(payload_width)
        self.spi.configuration_register_write(check_register)
        config_register = self.spi.configuration_register_read()
        self.assertTrue(config_register == check_register)
        write_payload = bytearray(payload_width)
        for i in range(0, payload_width):
            write_payload[i] = i + 2
        self.spi.write_transmit_payload(write_payload)
        read_payload = self.spi.read_transmit_payload()
        for i in range(0, payload_width):
            self.assertEqual(write_payload[i], read_payload[i])
        # Test 1 byte transfers
        payload_width = 1
        check_register.set_tx_pw(payload_width)
        self.spi.configuration_register_write(check_register)
        config_register = self.spi.configuration_register_read()
        self.assertTrue(config_register == check_register)
        write_payload = bytearray(payload_width)
        for i in range(0, payload_width):
            write_payload[i] = i + 3
        self.spi.write_transmit_payload(write_payload)
        read_payload = self.spi.read_transmit_payload()
        for i in range(0, payload_width):
            self.assertEqual(write_payload[i], read_payload[i])

    def test_transmit_address_read_write(self):
        """ Verify the TX_ADDRESS register functions. """
        write_address = 0xe7e7e7e7
        self.spi.write_transmit_address(write_address)
        read_address = self.spi.read_transmit_address()
        self.assertEqual(write_address, read_address)
        write_address = 0x18181818
        self.spi.write_transmit_address(write_address)
        read_address = self.spi.read_transmit_address()
        self.assertEqual(write_address, read_address)

    def test_receive_payload_read(self):
        """ Verify that values can be read from the receive payload register.
        This is difficult to test reliably as the data must be received and
        that needs antoher transmitter.  All we can test for here is that the
        number of bytes read is the same as the the number of bytes specified
        by the receive payload width register.
        """
        # Set config registers to power on defaults, 32 bytes of payload.
        check_register = Nrf905ConfigRegister()
        payload_width = 32
        self.spi.configuration_register_write(check_register)
        config_register = self.spi.configuration_register_read()
        self.assertTrue(config_register == check_register)
        read_payload = self.spi.read_receive_payload()
        self.assertEqual(len(read_payload), payload_width)
        # Test 14 byte payload
        payload_width = 14
        check_register.set_rx_pw(payload_width)
        self.spi.configuration_register_write(check_register)
        config_register = self.spi.configuration_register_read()
        self.assertTrue(config_register == check_register)
        read_payload = self.spi.read_receive_payload()
        self.assertEqual(len(read_payload), payload_width)
        # Test 1 byte transfers
        payload_width = 1
        check_register.set_rx_pw(payload_width)
        self.spi.configuration_register_write(check_register)
        config_register = self.spi.configuration_register_read()
        self.assertTrue(config_register == check_register)
        read_payload = self.spi.read_receive_payload()
        self.assertEqual(len(read_payload), payload_width)

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
            # print("tcc:", test[0], test[1], test[2])
            self.spi.channel_config(test[0], test[1], test[2])
            # Update check_register with same data
            check_register.set_channel_number(test[0])
            check_register.set_hfreq_pll(test[1])
            check_register.set_pa_pwr(test[2])
            # Read back and verify expected data matches
            config_register = self.spi.configuration_register_read()
            # config_register.print()
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


if __name__ == '__main__':
    unittest.main()
