#!/usr/bin/env python3

import pigpio

class Nrf905Spi:
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
    SPI_BUS_0_FLAGS = 0
    SPI_BUS_1_FLAGS = 0
    SPI_SCK_HZ = 1 * 1000 * 1000  # Set to 1MHz.  10MHz max. (data sheet)
    
    # pigpio SPI flag values
    SPI_MODE = 0  # nRF905 supports SPI mode 0 only. 2 bits
    SPI_CE_ACTIVE_HIGH = 0 # nRF905 active low. 1 bit
    SPI_CE_PIN = 0 # Use SPIx_CE0_N. 1 bit
    SPI_USE_AUX = 0 # Use main for RPi1A/B. 1 bit
    SPI_3WIRE = 0  # nRF905 is 4 wire. 1 bit
    SPI_TX_LSB_FIRST = 0  # nRF905 is MSB first. 1 bit
    SPI_RX_LSB_FIRST = 0  # nRF905 is MSB first. 1 bit
    SPI_AUX_WORD_SIZE = 0  # Using main SPI bus. 6 bits

    # nRF905 SPI instructions (table 13)
    INSTRUCTION_W_CONFIG = 0b00000000
    INSTRUCTION_R_CONFIG = 0b00010000
    INSTRUCTION_W_TX_PAYLOAD = 0b00100000
    INSTRUCTION_R_TX_PAYLOAD = 0b00100001
    INSTRUCTION_W_TX_ADDRESS = 0b00100010
    INSTRUCTION_R_TX_ADDRESS = 0b00100011
    INSTRUCTION_R_RX_PAYLOAD = 0b00100100
    INSTRUCTION_CHANNEL_CONFIG = 0b10000000

    def __set_spi_flags(self, mode):
        flags = 0
        if 0 <= mode <= 3:
            flags = mode
        return flags

    def __init__(self, pi, spi_bus):
        # Width of nRF905 registers. Defaults set to chip defaults.
        self.__receive_address_width = 0b100  # 4 bytes
        self.__transmit_address_width = 0b100   # 4 bytes
        self.__receive_payload_width = 0b100000  # 32 bytes
        self.__transmit_payload_width = 0b100000  # 32 bytes
        # The last value of the status register.
        self.__status_register = 0
        # Open SPI device
        self.__spi_handle = 0
        # Mode 1 works even though the datasheet says mode 0.
        spi_flags = self.__set_spi_flags(1)
        if spi_bus == 0:
            self.__spi_bus = 0
        elif spi_bus == 1:
            # Only supported on model 2 and later.
            self.__hw_version = pi.get_hardware_revision()
            if self.__hw_version >= 2:
                self.__spi_bus = 1
        else:
            raise ValueError("spi_bus out of range")
        # Open using validated SPI bus.
        if self.__spi_bus == -1:
            raise ValueError("spi_bus value not supported for this board")
        else:
            self.__spi_handle = pi.spi_open(self.__spi_bus, self.SPI_SCK_HZ, spi_flags)

    def close(self, pi):
        pi.spi_close(self.__spi_handle)

    def configuration_register_write(self, pi, data):
        """ Writes data to the RF configuration register.
            Raises ValueError exception if data does not contain 10 bytes.
            data must also be a bytearray.
        """
        if len(data) == 10:
            command = bytearray(11)
            # Prepend the instruction for writing all bytes to the config 
            # register.  The 4 least significant bytes are set to 0 so all 
            # bytes are written to. 
            command[0] = self.INSTRUCTION_W_CONFIG
            # Copy the rest of the data into the command.
            command[1:1 + len(data)] = data
            # Write the command to the config register.
            pi.spi_write(self.__spi_handle, command)
        else:
            raise ValueError("data must contain 10 bytes")

    def configuration_register_read(self, pi):
        """ Returns an array of 10 bytes read from the RF configuration register.
            If the read was not successful, returns empty array.
        """
        # Create empty bytearray that contains the command (first element)
        # followed by 10 empty bytes to clock through the 10 bytes of the config
        # register.
        command = bytearray(11)
        command[0] = self.INSTRUCTION_R_CONFIG
        (count, data) = pi.spi_xfer(self.__spi_handle, command)
        if count < 0:
            data = []
        else:
            # The first byte received is the status register.
            self.__status_register = data.pop(0)
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

    # TODO add named fields for the address and payload field widths. 
    def configuration_register_create(self, frequency_mhz, rx_address, crc_bits):
        """ Creates an array of data bytes from the given parameters suitable for
        writing to the device.
        crc_bits is one of 0, 8, 16.
        """
        register = bytearray(10)
        frequency_bits = self.__frequency_to_bits(frequency_mhz)
        register[0] = frequency_bits[0]
        register[1] = frequency_bits[1]
        # Byte 1 also has:
        # PA_PWR.  Use lowset setting, 0b00000000
        # RX_RED_PWR. Normal operation = 0
        # AUTO_RETRAN 0 = no auto retransmit.
        # All 0 for now so nothing to do.
        register[1] |= 0b00000000
        # Byte 2 TX_AFW = 0b01110000, RX_AFW = 0b00000111
        # Use 4 byte address widths for both.
        register[2] = 0b01000100
        # Byte 3. RX_PW 1 to 32. Set to 32 byte for now.
        register[3] = 32
        # Byte 4. TX_PW 1 to 32. Set to 32 byte for now.
        register[4] = 32
        # Bytes 5 to 8, the RX address.
        register[5] = rx_address & 0x000000ff
        register[6] = (rx_address & 0x0000ff00) >> 8
        register[7] = (rx_address & 0x00ff0000) >> 16
        register[8] = (rx_address & 0xff000000) >> 24
        # Byte 9
        # XOF is 16MHz, 0b00011000
        # UP_CLK_EN = 0, UP_CLK_FREQ = 00
        register[9] = 0b00011000
        # crc_bits is used to set CRC_EN (bit 6) and CRC_MODE (bit 7).
        if crc_bits == 0:
            # CRC_EN = 0 (disable)
            pass
        elif crc_bits == 8:
            # CRC_EN = 1 (enable)
            # CRC_MODE = 0 (8 bits)
            register[9] |= 0b01000000
        elif crc_bits == 16:
            # CRC_EN = 1 (enable)
            # CRC_MODE = 1 (16 bits)
            register[9] |= 0b11000000
        else:
            raise ValueError("crc_bits must be one of 0, 8, 16.")
        return register

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

    def write_transmit_payload(self, pi, payload):
        pass

    def read_transmit_payload(self, pi, payload):
        pass

    def write_transmit_address(self, pi, address):
        """ Writes the value of address to the transmit address register.
        Multi-byte values are transmitted LSB first, so the address
        needs to be broken down into bytes before sending.
        """
        # Create the array of bytes to send.
        command = bytearray(self.__transmit_address_width + 1)
        command[0] = self.INSTRUCTION_W_TX_ADDRESS
        for i in range(0, self.__transmit_address_width):
            byte = address & 0x000000FF
            data.append(byte)
            address >>= 8
        print("wta:", address, data)
        # Send the bytes.
        (count, status) = pi.spi_xfer(self.__spi_handle, data)
        # There should only be one byte received, the value of the status register.
        print("wta:", count, status)
        self.__status_register = status

    def read_transmit_address(self, pi):
        """ Returns a 32 bit value representing the address. """
        # Send the instruction to read the TX ADDRESS register.
        # Also needs a 0 byte for each of the bytes to read.
        command_width = self.__receive_address_width + 1
        command = bytearray(command_width)
        command[0] = self.INSTRUCTION_R_TX_ADDRESS
        (count, data) = pi.spi_xfer(self.__spi_handle, command)
        print("rta:", count, data)
        # The first byte received is the status register.
        self.__status_register = data[0]
        print("rts status", self.__status_register)
        # What is left is the address in reverse order.
        address = 0
        for i in range(1, len(data)):
            address = data[i]
            address <<= 8
        return address

    def read_receive_payload(self, pi):
        pass

    def set_channel_config(self, pi, channel, hfreq_pll, pa_pwr):
        pass

    def get_status_register(self):
        """Gets the last read value of the status register. """
        return self.__status_register

