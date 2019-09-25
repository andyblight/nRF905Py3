#!/usr/bin/env python3

import unittest

from nrf905.nrf905_config import Nrf905ConfigRegister


class TestNrf905SpiNc(unittest.TestCase):

    def test_config_register_init_get(self):
        """ Test the methods: __init__(), get().  """ 
        # Create the object.
        register = Nrf905ConfigRegister()
        # Verify default values are set. 
        register_bytes = register.get_all()
        self.assertEqual(register_bytes[0], 0x6C)
        self.assertEqual(register_bytes[1], 0x00)
        self.assertEqual(register_bytes[2], 0x44)
        self.assertEqual(register_bytes[3], 0x20)
        self.assertEqual(register_bytes[4], 0x20)
        self.assertEqual(register_bytes[5], 0xE7)
        self.assertEqual(register_bytes[6], 0xE7)
        self.assertEqual(register_bytes[7], 0xE7)
        self.assertEqual(register_bytes[8], 0xE7)
        self.assertEqual(register_bytes[9], 0xE7)

    def test_config_register_set_reset(self):
        """ Test the methods: set(), reset().  """ 
        register = Nrf905ConfigRegister()
        register_bytes = register.get_all()
        register_bytes[0] = 0x00
        register_bytes[4] = 0x44
        register_bytes[9] = 0x99
        register.set_all(register_bytes)
        register_bytes = register.get_all()
        self.assertEqual(register_bytes[0], 0x00)
        self.assertEqual(register_bytes[1], 0x00)
        self.assertEqual(register_bytes[2], 0x44)
        self.assertEqual(register_bytes[3], 0x20)
        self.assertEqual(register_bytes[4], 0x44)
        self.assertEqual(register_bytes[5], 0xE7)
        self.assertEqual(register_bytes[6], 0xE7)
        self.assertEqual(register_bytes[7], 0xE7)
        self.assertEqual(register_bytes[8], 0xE7)
        self.assertEqual(register_bytes[9], 0x99)
        register.reset()
        self.assertEqual(register_bytes[0], 0x6C)
        self.assertEqual(register_bytes[1], 0x00)
        self.assertEqual(register_bytes[2], 0x44)
        self.assertEqual(register_bytes[3], 0x20)
        self.assertEqual(register_bytes[4], 0x20)
        self.assertEqual(register_bytes[5], 0xE7)
        self.assertEqual(register_bytes[6], 0xE7)
        self.assertEqual(register_bytes[7], 0xE7)
        self.assertEqual(register_bytes[8], 0xE7)
        self.assertEqual(register_bytes[9], 0xE7)

    def test_set_byte(self):
        """ Tests the set_byte function. """
        register = Nrf905ConfigRegister()
        # Exact mask, no shifting, single bit
        value = 1
        mask = 0x01
        byte_value = 0x00
        result = register.set_byte(value, mask, byte_value)
        self.assertEqual(result, 0x01)
        # Exact mask, no shifting, 2 bits.
        value = 3
        mask = 0x03
        byte_value = 0x00
        result = register.set_byte(value, mask, byte_value)
        self.assertEqual(result, 0x03)
        # Exact mask, 1 bit shift, 2 bits.
        value = 3
        mask = 0x06
        byte_value = 0x00
        result = register.set_byte(value, mask, byte_value)
        self.assertEqual(result, 0x06)
        # Exact mask, 1 bit shift, 2 bits.
        value = 2
        mask = 0x18
        byte_value = 0x03
        result = register.set_byte(value, mask, byte_value)
        self.assertEqual(result, 0x13)


    def test_config_register_channel_number(self):
        register = Nrf905ConfigRegister()
        channel_number = register.get_channel_number()
        self.assertEqual(channel_number, 0x6C)
        register.set_channel_number(0x1FF)
        channel_number = register.get_channel_number()
        self.assertEqual(channel_number, 0x1FF)
        register.set_channel_number(0x077)
        channel_number = register.get_channel_number()
        self.assertEqual(channel_number, 0x077)

    def test_config_register_auto_retran(self):
        register = Nrf905ConfigRegister()
        auto_retran = register.get_auto_retran()
        self.assertEqual(auto_retran, 0)
        register.set_auto_retran(1)
        auto_retran = register.get_auto_retran()
        self.assertEqual(auto_retran, 1)
        register.set_auto_retran(0)
        auto_retran = register.get_auto_retran()
        self.assertEqual(auto_retran, 0)

    def test_config_register_rx_red_pwr(self):
        register = Nrf905ConfigRegister()
        rx_red_pwr = register.get_rx_red_pwr()
        self.assertEqual(rx_red_pwr, 0)
        register.set_rx_red_pwr(1)
        rx_red_pwr = register.get_rx_red_pwr()
        self.assertEqual(rx_red_pwr, 1)
        register.set_rx_red_pwr(0)
        rx_red_pwr = register.get_rx_red_pwr()
        self.assertEqual(rx_red_pwr, 0)

    def test_config_register_pa_pwr(self):
        register = Nrf905ConfigRegister()
        pa_pwr = register.get_pa_pwr()
        self.assertEqual(pa_pwr, 0)
        register.set_pa_pwr(1)
        pa_pwr = register.get_pa_pwr()
        self.assertEqual(pa_pwr, 1)
        register.set_pa_pwr(0)
        pa_pwr = register.get_pa_pwr()
        self.assertEqual(pa_pwr, 0)

    def test_config_register_hfreq_pll(self):
        register = Nrf905ConfigRegister()
        hfreq_pll = register.get_hfreq_pll()
        self.assertEqual(hfreq_pll, 0)
        register.set_hfreq_pll(1)
        hfreq_pll = register.get_hfreq_pll()
        self.assertEqual(hfreq_pll, 1)
        register.set_hfreq_pll(0)
        hfreq_pll = register.get_hfreq_pll()
        self.assertEqual(hfreq_pll, 0)

    def test_config_register_tx_afw(self):
        register = Nrf905ConfigRegister()
        tx_afw = register.get_tx_afw()
        self.assertEqual(tx_afw, 4)
        register.set_tx_afw(1)
        tx_afw = register.get_tx_afw()
        self.assertEqual(tx_afw, 1)
        register.set_tx_afw(2)
        tx_afw = register.get_tx_afw()
        self.assertEqual(tx_afw, 2)
        with self.assertRaises(ValueError):
            register.set_tx_afw(0)
        with self.assertRaises(ValueError):
            register.set_tx_afw(3)
        with self.assertRaises(ValueError):
            register.set_tx_afw(5)

    def test_config_register_rx_afw(self):
        register = Nrf905ConfigRegister()
        rx_afw = register.get_rx_afw()
        self.assertEqual(rx_afw, 4)
        register.set_rx_afw(1)
        rx_afw = register.get_rx_afw()
        self.assertEqual(rx_afw, 1)
        register.set_rx_afw(2)
        rx_afw = register.get_rx_afw()
        self.assertEqual(rx_afw, 2)
        with self.assertRaises(ValueError):
            register.set_rx_afw(0)
        with self.assertRaises(ValueError):
            register.set_rx_afw(3)
        with self.assertRaises(ValueError):
            register.set_rx_afw(5)

    def test_config_register_rx_pw(self):
        register = Nrf905ConfigRegister()
        rx_pw = register.get_rx_pw()
        self.assertEqual(rx_pw, 32)
        register.set_rx_pw(1)
        rx_pw = register.get_rx_pw()
        self.assertEqual(rx_pw, 1)
        register.set_rx_pw(15)
        rx_pw = register.get_rx_pw()
        self.assertEqual(rx_pw, 15)
        with self.assertRaises(ValueError):
            register.set_rx_pw(0)
        with self.assertRaises(ValueError):
            register.set_rx_pw(33)

    def test_config_register_tx_pw(self):
        register = Nrf905ConfigRegister()
        tx_pw = register.get_tx_pw()
        self.assertEqual(tx_pw, 32)
        register.set_tx_pw(1)
        tx_pw = register.get_tx_pw()
        self.assertEqual(tx_pw, 1)
        register.set_tx_pw(15)
        tx_pw = register.get_tx_pw()
        self.assertEqual(tx_pw, 15)
        with self.assertRaises(ValueError):
            register.set_tx_pw(0)
        with self.assertRaises(ValueError):
            register.set_tx_pw(33)

    def test_config_register_crc_mode(self):
        register = Nrf905ConfigRegister()
        crc_mode = register.get_crc_mode()
        self.assertEqual(crc_mode, 1)
        register.set_crc_mode(0)
        crc_mode = register.get_crc_mode()
        self.assertEqual(crc_mode, 0)
        register.set_crc_mode(1)
        crc_mode = register.get_crc_mode()
        self.assertEqual(crc_mode, 1)

    def test_config_register_crc_en(self):
        register = Nrf905ConfigRegister()
        crc_en = register.get_crc_en()
        self.assertEqual(crc_en, 1)
        register.set_crc_en(0)
        crc_en = register.get_crc_en()
        self.assertEqual(crc_en, 0)
        register.set_crc_en(1)
        crc_en = register.get_crc_en()
        self.assertEqual(crc_en, 1)

    def test_config_register_up_clk_en(self):
        register = Nrf905ConfigRegister()
        up_clk_en = register.get_up_clk_en()
        self.assertEqual(up_clk_en, 1)
        register.set_up_clk_en(0)
        up_clk_en = register.get_up_clk_en()
        self.assertEqual(up_clk_en, 0)
        register.set_up_clk_en(1)
        up_clk_en = register.get_up_clk_en()
        self.assertEqual(up_clk_en, 1)

    def test_config_register_xof_mhz(self):
        register = Nrf905ConfigRegister()
        xof_mhz = register.get_xof_mhz()
        self.assertEqual(xof_mhz, 20)
        register.set_xof_mhz(4)
        xof_mhz = register.get_xof_mhz()
        self.assertEqual(xof_mhz, 4)
        register.set_xof_mhz(16)
        xof_mhz = register.get_xof_mhz()
        self.assertEqual(xof_mhz, 16)
        with self.assertRaises(ValueError):
            register.set_xof_mhz(0)
        with self.assertRaises(ValueError):
            register.set_xof_mhz(1)
        with self.assertRaises(ValueError):
            register.set_xof_mhz(3)
        with self.assertRaises(ValueError):
            register.set_xof_mhz(5)
        with self.assertRaises(ValueError):
            register.set_xof_mhz(21)

    def test_config_register_up_clk_freq_mhz(self):
        register = Nrf905ConfigRegister()
        up_clk_freq_mhz = register.get_up_clk_freq_mhz()
        self.assertEqual(up_clk_freq_mhz, 0.5)
        register.set_up_clk_freq_mhz(4)
        up_clk_freq_mhz = register.get_up_clk_freq_mhz()
        self.assertEqual(up_clk_freq_mhz, 4)
        register.set_up_clk_freq_mhz(2)
        up_clk_freq_mhz = register.get_up_clk_freq_mhz()
        self.assertEqual(up_clk_freq_mhz, 2)
        register.set_up_clk_freq_mhz(1)
        up_clk_freq_mhz = register.get_up_clk_freq_mhz()
        self.assertEqual(up_clk_freq_mhz, 1)
        register.set_up_clk_freq_mhz(0.5)
        up_clk_freq_mhz = register.get_up_clk_freq_mhz()
        self.assertEqual(up_clk_freq_mhz, 0.5)
        with self.assertRaises(ValueError):
            register.set_up_clk_freq_mhz(0)
        with self.assertRaises(ValueError):
            register.set_up_clk_freq_mhz(0.4)
        with self.assertRaises(ValueError):
            register.set_up_clk_freq_mhz(3)
        with self.assertRaises(ValueError):
            register.set_up_clk_freq_mhz(5)


if __name__ == '__main__':
    unittest.main()
