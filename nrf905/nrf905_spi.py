#!/usr/bin/env python3

import pigpio

from nrf905.nrf905_config import Nrf905ConfigRegister

class Nrf905Spi:
    """ Handles access to SPI bus and the nRF905 registers.
    Extracts from the data sheet.
        The device must be in a low power mode to access the SPI registers.
        Whenever CSN is set low the interface expects an instruction.
        Every new instruction must be started by a high to low transition on CSN.
        The content of the status register (S[7:0]) is always read to
        MISO after a high to low transition on CSN.
    """

    __CRYSTAL_FREQUENCY_HZ = 16 * 1000 * 1000  # 16MHz is on the board I'm using.

    # SPI pins are defaults for pigpio bus 0 (RPi 1 A&B only have SPI bus 0).
    __SPI_BUS_0_FLAGS = 0 
    __SPI_BUS_1_FLAGS = 0
    __SPI_SCK_HZ = 10 * 1000 * 1000  # Set to 10MHz.  10MHz max. (data sheet)

    # nRF905 SPI instructions (table 13)
    __INSTRUCTION_W_CONFIG = 0b00000000
    __INSTRUCTION_R_CONFIG = 0b00010000
    __INSTRUCTION_W_TX_PAYLOAD = 0b00100000
    __INSTRUCTION_R_TX_PAYLOAD = 0b00100001
    __INSTRUCTION_W_TX_ADDRESS = 0b00100010
    __INSTRUCTION_R_TX_ADDRESS = 0b00100011
    __INSTRUCTION_R_RX_PAYLOAD = 0b00100100
    __INSTRUCTION_CHANNEL_CONFIG = 0b10000000

    def __init__(self):
        self.__pi = None
        self.__spi_h = None
        self.__status = 0
        # Width of nRF905 registers. Defaults set to chip defaults.
        self.__receive_address_width = 0b100  # 4 bytes
        self.__transmit_address_width = 0b100   # 4 bytes
        self.__receive_payload_width = 0b100000  # 32 bytes
        self.__transmit_payload_width = 0b100000  # 32 bytes

    def open(self, pi):
        # print("open:", pi)
        self.__pi = pi
        # print("open self.__pi:", self.__pi)
        self.__spi_h = self.__pi.spi_open(0, self.__SPI_SCK_HZ, self.__SPI_BUS_0_FLAGS)
        # print("open self.__spi_h:", self.__spi_h)

    def close(self):
        # print("close: self.__pi:", self.__pi)
        self.__pi.spi_close(self.__spi_h)

    def status_register_get(self):
        """Returns the last read value of the status register. """
        return self.__status

    def send_command(self, b_command):
        """ Sends the command to the nRF905 and returns any results.
        If a valid transfer takes place:
            1. The internal copy of the status register is updated.
            2. The function returns a bytearray that contains the result.
        If the transfer fails, returns an empty bytearray.
        """
        # print("Command is 0x", b_command.hex())
        # print("send_command: self.__pi:", self.__pi)
        # print("send_command self.__spi_h:", self.__spi_h)
        (count, data) = self.__pi.spi_xfer(self.__spi_h, b_command)
        # print("Received", count, data)
        if count > 0:
            self.__status = data.pop(0)
            # print("Status 0x", self.__status)
            # print("Data bytes", len(data), "0x", data.hex())
        else:
            data = bytearray()
        return data

    def configuration_register_read(self):
        """ Command to read all 10 bytes of the configuration register.
        Returns an instance of Nrf905ConfigRegister.
        """
        command = bytearray(11)
        command[0] = self.__INSTRUCTION_R_CONFIG
        data = self.send_command(command)
        register = Nrf905ConfigRegister()
        register.set_all(data)
        return register

    def configuration_register_write(self, register):
        """ Writes the data from the register object to the RF configuration
        register.
        Raises ValueError exception if data does not contain 10 bytes.
        """
        # Update internal width variables.
        self.__receive_address_width = register.get_rx_afw()
        self.__transmit_address_width = register.get_tx_afw()
        self.__receive_payload_width = register.get_rx_pw()
        self.__transmit_payload_width = register.get_tx_pw()
        register_bytes = register.get_all()
        if len(register_bytes) == 10:
            command = bytearray(11)
            command[0] = self.__INSTRUCTION_W_CONFIG
            # Copy the rest of the data into the command.
            command[1:1 + len(register_bytes)] = register_bytes
            print("crw:", command)
            # Write the command to the config register.
            self.send_command(command)
        else:
            raise ValueError("register_bytes must contain exactly 10 bytes")

    def write_transmit_address(self, address):
        """ Writes the value of address to the transmit address register. """
        command = bytearray()
        command.append(self.__INSTRUCTION_W_TX_ADDRESS)
        command += address.to_bytes(self.__transmit_address_width, 'little')
        print("wta:", address, command)
        self.send_command(command)

    def read_transmit_address(self):
        """ Returns a 32 bit value representing the address. """
        # Send the instruction to read the TX ADDRESS register.
        # Also needs a 0 byte for each of the bytes to read.
        command = bytearray(self.__transmit_address_width + 1)
        command[0] = self.__INSTRUCTION_R_TX_ADDRESS
        data = self.send_command(command)
        address = int.from_bytes(data, 'little')
        return address

    def channel_config(self, channel_number, hfreq_pll, pa_pwr):
        """ Special command for fast setting of CH_NO, HFREQ_Pand PA_PWR in the
        CONFIGURATION REGISTER.  SPI command has structure:
            1000 pphc cccc cccc
        where: CH_NO= ccccccccc, HFREQ_PLL = h PA_PWR = pp
        """
        command = bytearray(2)
        command[0] = self.__INSTRUCTION_CHANNEL_CONFIG
        if 0 <= pa_pwr < 4:
            command[0] |= ((pa_pwr & 0x03) << 2)
        else:
            raise ValueError("Out of range: 0 <= pa_pwr < 4")
        if hfreq_pll:
            command[0] |= 0x02
        if 0 <= channel_number < 0x200:
            command[1] = (channel_number & 0xFF)
            if channel_number & 0x100:
                command[0] |= 1
        else:
            raise ValueError("Out of range: 0 <= channel_number < 0x200")
        # print("channel_config", command.hex())
        self.send_command(command)



# class Nrf905Spi:

#     def __init__(self, pi, spi_bus):
#         # Width of nRF905 registers. Defaults set to chip defaults.
#         self.__receive_address_width = 0b100  # 4 bytes
#         self.__transmit_address_width = 0b100   # 4 bytes
#         self.__receive_payload_width = 0b100000  # 32 bytes
#         self.__transmit_payload_width = 0b100000  # 32 bytes
#         # The last value of the status register.
#         self.__status_register = 0
#         # Set SPI bus, speed and flags.
#         self.__bus = 0
#         self.__sck_hz = 0
#         self.__flags = 0
#         self.__set_bus(spi_bus)
#         # Open using validated SPI bus.
#         self.__handle = pi.spi_open(self.__bus, self.__sck_hz, self.__flags)
#     def __set_flags(self):
#         """ See http://abyz.me.uk/rpi/pigpio/python.html#spi_open for details.
#         The nRF095 works with most values set to 0.
#         Only need to set the mode and bus values.
#         """
#         # Mode = 2.
#         self.__flags = 2
#         if self.__bus == 1:
#             # Set bit 8 = 1 for aux bus.
#             self.__flags |= 0x10

#     def __set_bus(self, bus):
#         """Sets bus, clock speed and flags. """
#         spi_bus = -1
#         if bus == 0:
#             spi_bus = 0
#         elif bus == 1:
#             # Only supported on model 2 and later.
#             self.__hw_version = pi.get_hardware_revision()
#             if self.__hw_version >= 2:
#                 spi_bus = 1
#         else:
#             raise ValueError(" SPI bus out of range")
#         if spi_bus == -1:
#             raise ValueError("SPI bus not supported for this board")
#         # Set vars now that bus has been validated.
#         self.__sck_hz = self.SPI_SCK_HZ
#         self.__bus = spi_bus
#         self.__set_flags()

#     def __frequency_to_bits(self, frequency):
#         """ Returns a pair of bytes correct values of CH_NO and HFREQ_PLL.
#         Raises exception if frequency is invalid.
#         Table 24 from data sheet gives these values.
#         The HFREQ_PLL is byte 1, bit 1 and CH_NO bit 8 is byte 1, bit 0.
#         So all that is needed it a tuple containing a frequency and two byte
#         values.
#         UK frequency ranges:
#             433.05 to 434.79
#             863.00 to 870.00
#         TODO Add more valid frequencies.
#         """
#         frequency_list = [
#             (430.0, (0b01001100, 0b00)),  # 430MHz
#             (433.1, (0b01101011, 0b00)),
#             (433.2, (0b01101100, 0b00)),
#             (433.7, (0b01111011, 0b00)),
#             (862.0, (0b01010110, 0b10)),  # 860MHz
#             (868.2, (0b01110101, 0b10)),
#             (868.4, (0b01110110, 0b10)),
#             (869.8, (0b01111101, 0b10)),
#             (902.2, (0b00011111, 0b11)),  # 900MHZ
#             (902.4, (0b00100000, 0b11)),
#             (927.8, (0b10011111, 0b11))
#         ]
#         result = (0,0)
#         for entry in frequency_list:
#             if entry[0] == frequency:
#                 result = entry[1]
#         if result == (0, 0):
#             raise ValueError("Frequency not found.")
#         return result

#     def write_transmit_payload(self, pi, payload):
#         pass

#     def read_transmit_payload(self, pi, payload):
#         pass


#     def read_receive_payload(self, pi):
#         pass

#     def set_channel_config(self, pi, channel, hfreq_pll, pa_pwr):
#         pass



