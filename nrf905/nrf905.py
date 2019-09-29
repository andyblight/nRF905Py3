#!/usr/bin/env python3

import queue

from nrf905.nrf905_spi import Nrf905Spi
from nrf905.nrf905_gpio import Nrf905Gpio

class Nrf905:
    """ The interface to control a nRF905 device.  This class does all the
    parameter and state checking as well as any buffering.
    The actual byte bashing is done in the modules Nrf905Gpio and Nrf905Spi.

    Example usage:

    def callback(data):
        print("Received:", data)

    def main():
        transceiver = Nrf905()
        transceiver.set_frequency(434.25)
        transceiver.set_rx_address(0x43454749)
        transceiver.set_tx_address(0x4345474a)
        transceiver.open(callback)
        quit = False
        while not quit:
            data = input("Enter data ('q' to quit) >")
            if data == "q" or data == "Q":
                quit = True
            else:
                transceiver.send(data)
        receiver.close()
    """

    def __init__(self):
        self.__channel = 0
        self.__hfreq_pll = 0
        self.__rx_address = 0
        self.__tx_address = 0
        self.__rx_callback = None
        self.__is_open = False
        
    def set_frequency(self, frequency_mhz):
        """ Sets the frequency for the device in MHz. """
        print("set_frequency:", frequency_mhz)
        if self.__is_open:
            raise StateError("Cannot change frequency when open.")
        else:
            (channel, hfreq_pll) = Nrf905ConfigRegister.frequency_to_channel(frequency_mhz)
            if channel < 0:
                raise ValueError("Invalid frequency.")
            else:
                self.__channel = channel
                self.__hfreq_pll = hfreq_pll

    def set_rx_address(self, address):
        """Sets the receive address. Must less than 4 bytes long. """
        print("set_rx_address:", address)
        if self.__is_open:
            raise StateError("Cannot change address when open.")
        else:
            if address.bit_length() > 32:
                raise ValueError("Address contains more than 32 bits.")
            else:
                self.__rx_address = address
    
    def set_tx_address(self, address)
        """Sets the transmit address. Must less than 4 bytes long. """
        print("set_tx_address:", address)
        if self.__is_open:
            raise StateError("Cannot change address when open.")
        else:
            if address.bit_length() > 32:
                raise ValueError("Address contains more than 32 bits.")
            else:
                self.__tx_address = address

    def open(self, callback):
        """ Creates the instances of Nrf905Spi and Nrf905Gpio.
        """
        print("open")
        if self.__is_open:
            raise StateError("Already open.")
        else:
            self.__rx_callback = callback

    def close(self):
        """ Releases the instances of Nrf905Spi and Nrf905Gpio.
        The nRF905 device is left in the state last used.
        """
        print("close")

    def send(self, data):
        """ Posts the data to the transmit queue in 32 byte packets.
        Each packet in the queue will be transmitted until the queue is empty.
        """
        print("send:", data)
        if not self.__is_open:
            raise StateError("Call Nrf905.open() first.")
        else:
            self.__rx_callback = callback
        
        
#     def open(self, frequency, callback=None):
#         # print("open")
#         if self.__is_open:
#             if callback:
#                 if self.__is_transmitter:
#                     raise StateError("open as transmitter")
#             else:
#                 if not self.__is_transmitter:
#                     raise StateError("open as receiver")
#         else:
#             if callback:
#                 print("open as receiver:", frequency, callback)
#                 self.__callback = callback
#                 self.__is_transmitter = False
#             else:
#                 print("open as transmitter", frequency)
#                 self.__is_transmitter = True
#             self.__hw_configure()
#             self.__is_open = True

#         self.__is_open = False
#         self.__is_transmitter = False
#         self.__default_pins = []
#         self.__active_pins = []
#         self.__spi_bus = 0  # Default to 0
#         self.__callback = None
#         self.__frequency = 0
#         self.__address = 0
#         self.__crc_mode = 16
#         self.set_pins(self.__default_pins)

#     def set_pins(self, pins):
#         # print("set_pins")
#         if self.__is_open:
#             raise StateError("Pins NOT set. Device in use.")
#         else:
#             self.__active_pins = pins
#             print("pins set", pins)

#     def set_spi_bus(self, bus):
#         # print("set_spi_bus")
#         if self.__is_open:
#             raise StateError("SPI bus NOT set. Device in use.")
#         else:
#             if bus == 0 or bus == 1:
#                 self.__spi_bus = 0
#                 print("SPI bus set", bus)
#             else:
#                 raise ValueError("Bus out of range")

#     def set_address(self, address):
#         # print("set_address")
#         if self.__is_open:
#             raise StateError("Address NOT set. Device in use.")
#         else:
#             if address >= 0:
#                 if address == 0 or address & 0xffffffff:
#                     self.__address = address
#                     print("Address set", address)
#                 else:
#                     raise ValueError("Address out of range")
#             else:
#                 raise ValueError("Address out of range")

#     def set_crc_mode(self, mode):
#         # print("set_crc_mode")
#         if self.__is_open:
#             raise StateError("CRC mode NOT set. Device in use.")
#         else:
#             if mode == 0 or mode == 8 or mode == 16:
#                 self.__crc_mode = mode
#                 print("CRC mode set", mode)
#             else:
#                 raise ValueError("CRC mode must be one of 0, 8, 16")

#     def set_frequency(self, frequency):
#         # print("set_frequency")
#         if self.__is_open:
#             raise StateError("Frequency NOT set. Device in use.")
#         else:
#             # TODO Verify frequency 
#             if mode == 0 or mode == 8 or mode == 16:
#                 self.__crc_mode = mode
#                 print("CRC mode set", mode)
#             else:
#                 raise ValueError("CRC mode must be one of 0, 8, 16")

#     def open(self, frequency, callback=None):
#         # print("open")
#         if self.__is_open:
#             if callback:
#                 if self.__is_transmitter:
#                     raise StateError("open as transmitter")
#             else:
#                 if not self.__is_transmitter:
#                     raise StateError("open as receiver")
#         else:
#             if callback:
#                 print("open as receiver:", frequency, callback)
#                 self.__callback = callback
#                 self.__is_transmitter = False
#             else:
#                 print("open as transmitter", frequency)
#                 self.__is_transmitter = True
#             self.__hw_configure()
#             self.__is_open = True

#     def write(self, data):
#         # print("write")
#         if self.__is_open:
#             if self.__is_transmitter:
#                 self.__hw_write(data)
#                 print("wrote", data)
#             else:
#                 raise StateError("Device in receive mode.")
#         else:
#             raise StateError("Device not ready.  Call open() first.")

#     def __hw_configure(self):
#         """ Uses member variables directly """
#         print("__hw_configure")

#     def __hw_write(self, data):
#         print("__hw_write", data)

#     def __hw_release(self):
#         print("__hw_release")


# class Error(Exception):
#     """Base class for exceptions in this module."""
#     pass


# class StateError(Error):
#     """ Exception raised when functions are called when in the wrong state.

#     Attributes:
#         message -- explanation of the error
#     """    
#     def __init__(self, message):
#         self.message = message

# import Queue
# import pigpio

# class Nrf905Hardware:
#     """ Controls the nRF905 module.
    
#     The nRF905 terms are used in this module.
#     """

#     CRYSTAL_FREQUENCY_HZ = 16 * 1000 * 1000  # 16MHz is on the board I'm using.
    
#     def __init__(self):
#         print("init")
#         self.__pi = pigpio.pi()
#         self.__gpio = Nrf905Gpio(self.__pi)
#         self.__spi = Nrf905Spi(self.__pi)
#         self.__receive_queue = Queue.Queue()

#     def term(self):
#         print("term")
#         self.__spi.term(self.__pi)
#         self.__gpio.term(self.__pi)
#         self.__pi.stop()

#     def open(self):
#         """ Set up the nRF905 module in power down mode. """
#         print("open")
#         if self.__pi.connected:
#             self.__gpio.set_mode(self.__pi, Nrf905Gpio.POWER_DOWN)
#             self.__spi.open()
#             self.__receive_queue = 0  # Clear the queue. 
#         else:
#             raise ProcessLookupError("Could not connect to pigpio daemon.")

#     def transmit(self, data):
#         """ Put into standby mode, write the data to be transmitted to the 
#         nRF905 and set mode to transmit.
#         If the data given is too bit to be transmitted in one burst, the data
#         is split into burst sized chunks and transmitted until all the data has
#         been sent.
#         """
#         print("transmit", data)
#         self.__gpio.set_mode(self.__pi, Nrf905Gpio.STANDBY)
#         # Write to registers
#         self.__gpio.set_mode(self.__pi, Nrf905Gpio.TRANSMIT)

#     def data_ready_callback(self):
#         """ When data is ready, drop out of receive mode, read the data from 
#         the SPI RX register, go back into receive mode and finally write the 
#         data to the rx queue.
#         """
#         print("drc")
#         self.__gpio.set_mode_standby(self.__pi)
#         data = self.__spi.read_rx_data(self.__pi)
#         self.__gpio.set_mode_receive(self.__pi)
#         for byte in data:
#             self.__receive_queue.put(byte)
#         print(data)

#     def receive(self, address):
#         print("receive", address)
#         self.__gpio.set_mode(self.__pi, Nrf905Gpio.STANDBY)
#         self.__gpio.set_data_ready_callback(self.__pi, self.data_ready_callback)
#         # Send data to registers for receive.
#         self.__spi.set_address(self.__pi, address)
#         self.__gpio.set_mode(self.__pi, Nrf905Gpio.RECEIVE)

#     def get_receive_data(self):
#         """ Returns a list of all bytes in the RX queue.  If the queue is empty,
#         returns empty list.
#         """
#         result = []
#         if len(self.__receive_queue) > 0:
#             while not self.__receive_queue.empty():
#                 byte = self.__receive_queue.get()
#                 result.append(byte)
#         return result

