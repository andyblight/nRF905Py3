#!/usr/bin/env python3

class Nrf905ConfigRegister:
    """ The config register class has many functions so made sense to move them
    out of the Nrf905Spi class.
    As the datasheet and most uses of this class revolve around the byte 
    values, use the bytearray internally.
    Function names for getters and setters match the datasheet names for the
    registers.
    """

    def __init__(self):
        """ Create an object with power on defaults. """
        self.registers = bytearray(10)
        self.reset()

    def __eq__(self, other):
        """ Equality operator """
        equal = True
        for i in range(0, len(self.registers)):
            if self.registers[i] != other.registers[i]:
                equal = False
                break
        return equal

    def reset(self):
        """ Reset the object to power on default values. """
        self.registers[0] = 0b01101100
        self.registers[1] = 0
        self.registers[2] = 0b01000100
        self.registers[3] = 0b00100000
        self.registers[4] = 0b00100000
        self.registers[5] = 0xE7
        self.registers[6] = 0xE7
        self.registers[7] = 0xE7
        self.registers[8] = 0xE7
        self.registers[9] = 0b11100111

    def print(self):
        """ Prints the values using data sheet names. """
        print("Configuration register contents:")
        print("CH_NO:", self.get_channel_number())
        print("AUTO_RETRAN:", self.get_auto_retran())
        print("RX_RED_PWR:", self.get_rx_red_pwr())
        print("PA_PWR:", self.get_pa_pwr())
        print("HFREQ_PLL:", self.get_hfreq_pll())
        print("TX_AFW:", self.get_tx_afw())
        print("RX_AFW", self.get_rx_afw())
        print("RX_PWR:", self.get_rx_pw())
        print("TX_PWR:", self.get_tx_pw())
        print("RX_ADDRESS:", hex(self.get_rx_address()))
        print("CRC_MODE:", self.get_crc_mode())
        print("CRC_EN:", self.get_crc_en())
        print("XOF:", self.get_xof_mhz())
        print("UP_CLK_EN:", self.get_up_clk_en())
        print("UP_CLK_FREQ:", self.get_up_clk_freq_mhz())

    def get_all(self):
        """ Return a bytearray representing the configuration registers. """
        return self.registers

    def set_all(self, registers):
        """ Sets the internal values from the given bytearray. """
        self.registers = registers

    def set_byte(self, value, mask, byte_value):
        # print("sb: ", value, mask, byte_value)
        result = byte_value
        # Clear all masked bits.
        result &= ~(mask)
        # Find least significant bit of mask
        lowest_bit_set = 0
        test_mask = mask
        for bit in range(0, 8):
            if test_mask & 0x01:
                lowest_bit_set = bit
                break
            test_mask >>= 1
        # Shift value into the right position
        value <<= lowest_bit_set
        # Set bits
        result |= value
        # print("sb: ", result)
        return result

    def get_channel_number(self):
        # print("gcn: ", self.registers[0], self.registers[1])
        channel_number = self.registers[0]
        if (self.registers[1] & 0x01):
            channel_number += 256
        # print("gcn: ", channel_number)
        return channel_number

    def set_channel_number(self, channel_number):
        ch_num = channel_number.to_bytes(2, 'little')
        # print("scn: ", channel_number, ch_num)
        self.registers[0] = ch_num[0]
        self.registers[1] = self.set_byte((ch_num[1] & 0x01), 0x01, self.registers[1])
        # print("scn: ", self.registers[0], self.registers[1])
        
    def get_auto_retran(self):
        result = 0
        if self.registers[1] & 0x20:
            result = 1
        return result

    def set_auto_retran(self, auto_retran):
        self.registers[1] = self.set_byte((auto_retran & 0x01), 0x20, self.registers[1])

    def get_rx_red_pwr(self):
        result = 0
        if self.registers[1] & 0x08:
            result = 1
        return result

    def set_rx_red_pwr(self, rx_red_pwr):
        self.registers[1] = self.set_byte((rx_red_pwr & 0x01), 0x08, self.registers[1])

    def get_pa_pwr(self):
        result = self.registers[1] & 0x0c
        result >>= 2
        return result

    def set_pa_pwr(self, pa_pwr):
        self.registers[1] = self.set_byte((pa_pwr & 0x03), 0x0C, self.registers[1])

    def get_hfreq_pll(self):
        result = 0
        if self.registers[1] & 0x02:
            result = 1
        return result

    def set_hfreq_pll(self, hfreq_pll):
        self.registers[1] = self.set_byte((hfreq_pll & 0x01), 0x02, self.registers[1])

    def get_tx_afw(self):
        result = self.registers[2] & 0x70
        result >>= 4
        return result

    def set_tx_afw(self, tx_afw):
        if tx_afw == 1 or tx_afw == 2 or tx_afw ==4:
            self.registers[2] = self.set_byte((tx_afw & 0x07), 0x70, self.registers[2])
        else:
            raise ValueError("tx_afw must be one of 1, 2 or 4")

    def get_rx_afw(self):
        result = self.registers[2] & 0x07
        return result

    def set_rx_afw(self, rx_afw):
        if rx_afw == 1 or rx_afw == 2 or rx_afw ==4:
            self.registers[2] = self.set_byte((rx_afw & 0x07), 0x07, self.registers[2])
        else:
            raise ValueError("rx_afw must be one of 1, 2 or 4")

    def get_rx_pw(self):
        result = self.registers[3] & 0x3F
        return result

    def set_rx_pw(self, rx_pw):
        if 1 <= rx_pw <= 32:
            self.registers[3] = self.set_byte((rx_pw & 0x3F), 0x3F, self.registers[3])
        else:
            raise ValueError("rx_pw must be in range 1 to 32")

    def get_tx_pw(self):
        result = self.registers[4] & 0x3F
        return result

    def set_tx_pw(self, tx_pw):
        if 1 <= tx_pw <= 32:
            self.registers[4] = self.set_byte((tx_pw & 0x3F), 0x3F, self.registers[4])
        else:
            raise ValueError("tx_pw must be in range 1 to 32")

    def get_rx_address(self):
        # TODO This should only read the bytes that are specified in the width.
        regs = self.registers[5:9]
        # print("gra regs", regs)
        address = int.from_bytes(regs, 'little')
        # print("gra test", hex(address))
        return address

    def set_rx_address(self, address):
        # TODO This should only accept the number of bytes that are specified in
        # the width.
        # Reg 5 = byte 0, reg 6 = byte 1, reg 7 = byte 2, reg 8 = byte 3
        # print("sra", hex(address))
        regs = address.to_bytes(4, 'little')
        # print("sra bytes", regs)
        for i in range(0, 4):
            self.registers[5 + i] = regs[i]
        # print("sra::", self.registers)

    def get_crc_mode(self):
        result = 0
        if self.registers[9] & 0x80:
            result = 1
        return result

    def set_crc_mode(self, crc_mode):
        self.registers[9] = self.set_byte((crc_mode & 0x01), 0x80, self.registers[9])

    def get_crc_en(self):
        result = 0
        if self.registers[9] & 0x40:
            result = 1
        return result

    def set_crc_en(self, crc_en):
        self.registers[9] = self.set_byte((crc_en & 0x01), 0x40, self.registers[9])

    def get_xof_mhz(self):
        """ Returns value in whole MHz """
        result = self.registers[9] & 0x38
        result >>= 3
        result_mhz = (result * 4) + 4
        return result_mhz

    def set_xof_mhz(self, xof_mhz):
        if xof_mhz == 4 or xof_mhz == 8 or xof_mhz == 12 or xof_mhz == 16 or xof_mhz ==20:
            xof = bytearray(1)
            xof[0] = int((xof_mhz - 4) / 4)
            self.registers[9] = self.set_byte(xof[0], 0x38, self.registers[9])
        else:
            raise ValueError("xof_mhz must be one of 4, 8, 12, 16 or 20")

    def get_up_clk_en(self):
        result = 0
        if self.registers[9] & 0x04:
            result = 1
        return result

    def set_up_clk_en(self, up_clk_en):
        self.registers[9] = self.set_byte((up_clk_en & 0x01), 0x04, self.registers[9])

    def get_up_clk_freq_mhz(self):
        """ Returns value in whole MHz """
        result = self.registers[9] & 0x03
        if result == 3:
            result_mhz = 0.5
        elif result == 2:
            result_mhz = 1
        elif result == 1:
            result_mhz = 2
        else:
            result_mhz = 4
        return result_mhz

    def set_up_clk_freq_mhz(self, up_clk_freq_mhz):
        up_clk_freq = bytearray(1)
        if up_clk_freq_mhz == 0.5:
            up_clk_freq[0] = 3
        elif up_clk_freq_mhz == 1:
            up_clk_freq[0] = 2
        elif up_clk_freq_mhz == 2:
            up_clk_freq[0] = 1
        elif up_clk_freq_mhz == 4:
            up_clk_freq[0] = 0
        else:
            raise ValueError("up_clk_freq_mhz must be one of 0.5, 1, 2, 4")
        self.registers[9] = self.set_byte(up_clk_freq[0], 0x03, self.registers[9])

    def board_defaults(self):
        """ Set the contents of the registers to values that work for the device
        being used.  This can vary from supplier to supplier so may need to be
        changed.
        """
        self.reset()
        # 16 Mhz crystal
        self.set_xof_mhz(16)
        # Output clock not used.
        self.set_up_clk_en(0)

    @staticmethod
    def frequency_to_channel(frequency_mhz):
        """ Convert the given frequency in MHz to a channel and hfreq_pll value.
        If the given frequency is out of range, channel will = -1.
        If the given frequency is in range but not an exact match, the channel
        nearest to the given frequency will be returned.
        Output frequency = (422.4 + ( CH_NO / 10)) * ( 1 + HFREQ_PLL) MHz
        where CH_NO in range 0 to 511 and HFREQ_PLL is 1 or 0.
        Frequency ranges are 422.4 to 473.5MHz and 844.8 to 947MHz.
        """
        channel = -1  # Error value
        hfreq_pll = 0
        if 422.4 <= frequency_mhz <= 473.5 or 844.8 <= frequency_mhz <= 947:
            # Valid range so calculate bit patterns.
            if frequency_mhz >= 800:
                hfreq_pll = 1
                freq = frequency_mhz / 2
            else:
                freq = frequency_mhz
            freq -= 422.4
            channel = int(freq * 10)
        return (channel, hfreq_pll)

    @staticmethod
    def is_valid_uk(frequency_mhz):
        """ Returns True if the given frequency is legal in the UK. """
        result = False
        # 433MHz band.  Full range is 433.00 to 434.775MHz.
        # Radio hams use some of the channels for repeaters.
        # Exclude channels 1 to 11 and 62 to 69.
        if 433.4 <= frequency_mhz <= 434.5:
            result = True
        # 866MHz band
        if 863.0 <= frequency_mhz <= 870.0:
            result = True
        return result
