#!/usr/bin/env python3

import pigpio

class nrf905spi:
    """ Handles access to SPI bus and the nRF905 registers.
    Extracts from the data sheet.
        The device must be in a low power mode to access the registers.
        Whenever CSN is set low the interface expects an instruction. 
        Every new instruction must be started by a high to low transition on CSN.
        The content of the status register (S[7:0]) is always read to
        MISO after a high to low transition on CSN.

    """

    CRYSTAL_FREQUENCY_HZ = 16 * 1000 * 1000  # 16MHz is on the board I'm using.
    
    # SPI pins are defaults for pigpio bus 0 (RPi 1 A&B only have SPI bus 0).
    SPI_BUS = 0
    SPI_SCK_HZ = 1 * 1000 * 1000  # 10MHz max. (data sheet)
    
    # pigpio SPI flag values
    SPI_MODE = 0  # nRF905 supports SPI mode 0 only. 2 bits
    SPI_CE_ACTIVE_HIGH = 0 # nRF905 active low. 1 bit
    SPI_CE_PIN = 0 # Use SPIx_CE0_N. 1 bit
    SPI_USE_AUX = 0 # Use main for RPi1A/B. 1 bit
    SPI_3WIRE = 0  # nRF905 is 4 wire. 1 bit
    SPI_TX_LSB_FIRST = 0  # nRF905 is MSB first. 1 bit
    SPI_RX_LSB_FIRST = 0  # nRF905 is MSB first. 1 bit
    SPI_AUX_WORD_SIZE = 0  # Using main SPI bus. 6 bits

    def __init__(self, pi):
        self.__spi_handle = 0
        # As this driver is using SPI0, all values are 0.  Add code here if any 
        # of the values need to be changed. 
        spi_flags = 0
        # Open SPI device
        self.__spi_handle = pi.spi_open(self.SPI_BUS, self.SPI_SCK_HZ, spi_flags)

    def close(self, pi):
        pi.spi_close(self.__spi_handle)

    def configuration_register_write(self, pi, data):
        """ Writes data to the RF configuration register.
            Raises ValueError exception if data does not contain 10 bytes.
        """
        if len(data) == 10:
            # Prepend the instruction for writing all bytes to the config 
            # register is 0.
            data.insert(0, 0)
            # Write the data to the register.
            pi.spi_write(self.__spi_handle, data)
        else:
            raise ValueError("data must contain 10 bytes")

    def configuration_register_read(self, pi):
        """ Returns an array of 10 bytes read from the RF configuration register.
            If the read was not successful, returns empty array.
            We need to write an instruction byte before reading back the data
            so we use spi_xfer instead of spi_read.
            The command for reading all bytes is 0x10.
        """
        (count, data) = pi.spi_xfer(self.__spi_handle, b'\0x10')
        if count < 0:
            data = []
        return data

    def configuration_register_print(self, data):
        # Prints the values using data sheet names.
        if len(data) == 10:
            channel_number = ((data[1] & 0x01) * 256) + data[0]
            print()
            print("CH_NO:", channel_number)
            print("AUTO_RETRAN:", data[1] & 0x10)
            print("RX_RED_PWR:", data[1] & 0x10)
            print("PA_PWR:", data[1] & 0x10)
            print("HFREQ_PLL:", data[1] & 0x10)
            print("TX_AFW:", data[2] & 0x70)
            print("RX_AFW", data[2] & 0x07)
            print("RX_PWR:", data[3] & 0x3f)
            print("TX_PWR:", data[4] & 0x3f)
            print("RX_ADDRESS:", data[8], data[7], data[6], data[5])
            print("CRC_MODE:", data[9] & 0x80)
            print("CRC_EN:", data[9] & 0x40)
            print("XOF:", data[9] & 0x38)
            print("UP_CLK_EN:", data[9] & 0x04)
            print("UP_CLK_FREQ:", data[9] & 0x03)
        else:
            raise ValueError("data must contain 10 bytes")

    def configuration_register_create(self, frequency_mhz, rx_address, crc_bits):
        """ Creates an array of data bytes from the given parameters suitable for
        writing to the device.
        crc_bits is one of 0, 8, 16.
        """
        frequency_bits = self.__frequency_to_bits(frequency_mhz)
        byte_0 = frequency_bits[0]
        byte_1 = frequency_bits[1]
        # Byte 1 also has:
        # PA_PWR.  Use lowset settuing, 0b00000000
        # RX_RED_PWR. Normal operation = 0
        # AUTO_RETRAN 0 = no auto retransmit.
        # All 0 for now so nothing to do.
        byte_1 |= 0b00000000
        # Byte 2 TX_AFW = 0b01110000, RX_AFW = 0b00000111
        # Use 4 byte address widths for both.
        byte_2 = 0b01000100
        # Byte 3. RX_PW 1 to 32. Set to 1 byte for now.
        byte_3 = 1
        # Byte 4. TX_PW 1 to 32. Set to 1 byte for now.
        byte_4 = 1
        byte_5 = rx_address & 0x000000ff
        byte_6 = (rx_address & 0x0000ff00) >> 8
        byte_7 = (rx_address & 0x00ff0000) >> 16
        byte_8 = (rx_address & 0xff000000) >> 24
        # Byte 9
        # XOF is 16MHz, 0b00011000
        # UP_CLK_EN = 0, UP_CLK_FREQ = 00
        byte_9 = 0b00011000
        if crc_bits == 8:
            byte_9 |= 0b01000000
        if crc_bits == 16:
            byte_9 |= 0b11000000
        result = [byte_0, byte_1, byte_2, byte_3, byte_4, byte_5, byte_6, byte_7, byte_8, byte_9]
        return result

    def __frequency_to_bits(self, frequency):
        """ Returns a pair of bytes correct values of CH_NO and HFREQ_PLL.
        Raises exception if frequency is invalid.
        Table 24 from data sheet gives these values.
        The HFREQ_PLL is byte 1, bit 1 and CH_NO bit 8 is byte 1, bit 0.
        So all that is needed it a tuple containing a frequency and two byte
        values.
        UK frequency ranges:
            433.05 to 434.79
            863.00 to 870.00
        TODO Add more valid frequencies.
        """
        frequency_list = [
            (430.0, (0b01001100, 0b00)),  # 430MHz
            (433.1, (0b01101011, 0b00)),
            (433.2, (0b01101100, 0b00)),
            (433.7, (0b01111011, 0b00)),
            (862.0, (0b01010110, 0b10)),  # 860MHz
            (868.2, (0b01110101, 0b10)),
            (868.4, (0b01110110, 0b10)),
            (869.8, (0b01111101, 0b10)),
            (902.2, (0b00011111, 0b11)),  # 900MHZ
            (902.4, (0b00100000, 0b11)),
            (927.8, (0b10011111, 0b11))
        ]
        result = (0,0)
        for entry in frequency_list:
            if entry[0] == frequency:
                result = entry[1]
        if result == (0, 0):
            raise ValueError("Frequency not found.")
        return result
