#!/usr/bin/env python3

import pigpio

class nrf905spi:
    """ Handles access to SPI bus and the nRF905 registers.
    """

    CRYSTAL_FREQUENCY_HZ = 16 * 1000 * 1000  # 16MHz is on the board I'm using.
    
    # SPI pins are defaults for pigpio bus 0 (RPi 1 A&B only have SPI bus 0).
    SPI_BUS = 0
    SPI_SCK_HZ = 1 * 1000 * 1000  # 10MHz max. (data sheet)

    def __init__(self, pi):
        self.__spi_handle = 0
        # nRF905 supports SPI mode 0.
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
            # Write the address of the register.
            pi.spi_write(self.__spi_handle, data)
            # Write the data to the register.
            pi.spi_write(self.__spi_handle, data)
        else:
            raise ValueError("data must contain 10 bytes")

    def configuration_register_read(self, pi):
        """ Returns an array of 10 bytes read from the RF configuration register.
            If the read was not successful, returns empty array.
        """
        # Write the address of the register.
        
        # Read the data from the register.
        bytes_to_read = 10
        (count, data) = pi.spi_read(self.__spi_handle, bytes_to_read)
        if not count == bytes_to_read:
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

    def configuration_register_create(self, frequency_mhz, rx_address, crc_mode):
        # Creates an array of data bytes from the given parameters suitable for
        # writing to the device.
        frequency_bits = self.__frequency_to_bits(frequency_mhz)
        byte_0 = frequency_bits[0]
        byte_1 = frequency_bits[1]
        byte_2 = 0
        byte_3 = 0
        byte_4 = 0
        byte_5 = 0xff
        byte_6 = 0
        byte_7 = 0
        byte_8 = 0
        byte_9 = 0
        result = [byte_0, byte_1, byte_2, byte_3, byte_4, byte_5, byte_6, byte_7, byte_8, byte_9]
        return result

    def __frequency_to_bits(self, frequency):
        """ Returns a pair of bytes correct values of CH_NO and HFREQ_PLL.
        Raises exception if frequency is invalid.
        Table 24 from data sheet gives these values.
        The HFREQ_PLL is byte 1, bit 1 and CH_NO bit 8 is byte 1, bit 0.
        So all that is needed it a tuple containing a frequency and two byte
        values.
        """
        frequency_dict = dict([
            (430.0, (0b01001100, 0b00)),  # 430 MHz
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
        ])
        result = (0,0)
        for key, value in frequency_dict:
            if key == frequency:
                result = value
        if result == (0, 0):
            raise ValueError("Frequency not found.")
        return result
