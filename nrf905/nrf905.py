#!/usr/bin/env python3

import queue

from nrf905.nrf905_spi import Nrf905Spi
from nrf905.nrf905_gpio import Nrf905Gpio


def data_ready_callback(data):
    print("drc:", data)

def carrier_detect_callback(data):
    print("cdc:", data)

def address_matched_callback(data):
    print("amc:", data)


class Nrf905:
    """ The interface to control a nRF905 device.  This class does all the
    parameter and state checking as well as any buffering.
    The actual byte bashing is done in the modules Nrf905Gpio and Nrf905Spi.

    Example usage:

    def callback(data):
        print("Received:", data)

    def main():
        transceiver = Nrf905()
        # Must be set before open is called.
        transceiver.set_frequency(434.25)
        transceiver.set_rx_address(0x43454749)
        # Optional to set before open is called.
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
        # nRF905 properties
        self._channel = -1
        self._hfreq_pll = -1
        self._rx_address = -1
        self._tx_address = 0
        # Properties to make the class work.
        self._rx_callback = None
        self._is_open = False
        self._queue = None
        self._thread = None
        self._pi = None
        self._spi = None
        self._gpio = None
        
    def set_frequency(self, frequency_mhz):
        """ Sets the frequency for the device in MHz. """
        print("set_frequency:", frequency_mhz)
        if self._is_open:
            raise StateError("Cannot change frequency when open.")
        else:
            if Nrf905ConfigRegister.is_valid_uk(frequency_mhz):
                (channel, hfreq_pll) = Nrf905ConfigRegister.frequency_to_channel(frequency_mhz)
                if channel < 0:
                    raise ValueError("Invalid frequency.")
                else:
                    self._channel = channel
                    self._hfreq_pll = hfreq_pll
            else:
                raise ValueError("Frequency not valid in UK.")

    def set_rx_address(self, address):
        """ Sets the receive address. Must less than 4 bytes long. """
        print("set_rx_address:", address)
        if self._is_open:
            raise StateError("Cannot change address when open.")
        else:
            if address.bit_length() > 32:
                raise ValueError("Address contains more than 32 bits.")
            else:
                self._rx_address = address
    
    def set_tx_address(self, address)
        """ Sets the transmit address. Must less than 4 bytes long. """
        print("set_tx_address:", address)
        if self._is_open:
            raise StateError("Cannot change address when open.")
        else:
            if address.bit_length() > 32:
                raise ValueError("Address contains more than 32 bits.")
            else:
                self._tx_address = address

    def open(self, callback):
        """ Creates the instances of Nrf905Spi and Nrf905Gpio.
        Applies previously set values to nRF905 device.
        Prepares callback for use.
        """
        print("open")
        if self._is_open:
            raise StateError("Already open.")
        else:
            # Frequency and RX address must be set before open is called.
            if self._channel == -1 or self._hfreq_pll == -1 or 
                    self._rx_address == -1:
                raise ValueError("Frequency and RX address must be set.")
            else:
                # Create SPI and GPIO objects.
                self._pi = pigpio.pi()
                self._gpio = Nrf905Gpio(self._pi)
                self._spi = Nrf905Spi()
                self._spi.open(self._pi)
                # Set up nRF905
                # Power down mode
                self._gpio.set_mode_power_down(self._pi)
                # Config register.  
                config = Nrf905ConfigRegister()
                config.board_defaults()
                config.set_channel_number(self._channel)
                config.set_hfreq_pll(self._hfreq_pll)
                config.set_rx_address(self._rx_address)
                self._spi.configuration_register_write(config)
                # The TX address can be set later.
                if self._tx_address != 0:
                    self.spi.write_transmit_address(write_address)
                # Callbacks
                self._gpio.set_callback(self._pi, Nrf905Gpio.DATA_READY, data_ready_callback)
                self._gpio.set_callback(self._pi, Nrf905Gpio.CARRIER_DETECT, carrier_detect_callback)
                self._gpio.set_callback(self._pi, Nrf905Gpio.ADDRESS_MATCHED, address_matched_callback)
                # Start thread
                self._queue = queue.Queue()
                self._thread = threading.Thread(target=_worker)
                self._thread.start()

    def close(self):
        """ Releases the instances of Nrf905Spi and Nrf905Gpio.
        The nRF905 device is left in the state last used.
        """
        print("close")
        # Close down thread nicely.
        self._queue.join()
        self._queue.put(None)
        self._thread.join()
        # Release objects.
        self._spi.close()
        self._pi.stop()

    def send(self, data):
        """ Posts the data to the transmit queue in 32 byte packets.
        Each packet in the queue will be transmitted until the queue is empty.
        """
        print("send:", data)
        if not self._is_open:
            raise StateError("Call Nrf905.open() first.")
        else:
            self._queue.put(data)

    def _worker(self):
        """ Wait for a packet. When a packet is ready, send the packet and 
        repeat.
        """
        while True:
            data = self._queue.get()
            if data is None:
                break
            self._send(data)
            self._queue.task_done()

    def _send(self, data):
            # TODO Change modes.
            self._spi.write_transmit_payload(data)



class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class StateError(Error):
    """ Exception raised when functions are called when in the wrong state.
    Attributes:
        message -- explanation of the error
    """    
    def _init_(self, message):
        self.message = message


#     def open(self, frequency, callback=None):
#         # print("open")
#         if self._is_open:
#             if callback:
#                 if self._is_transmitter:
#                     raise StateError("open as transmitter")
#             else:
#                 if not self._is_transmitter:
#                     raise StateError("open as receiver")
#         else:
#             if callback:
#                 print("open as receiver:", frequency, callback)
#                 self._callback = callback
#                 self._is_transmitter = False
#             else:
#                 print("open as transmitter", frequency)
#                 self._is_transmitter = True
#             self._hw_configure()
#             self._is_open = True

#         self._is_open = False
#         self._is_transmitter = False
#         self._default_pins = []
#         self._active_pins = []
#         self._spi_bus = 0  # Default to 0
#         self._callback = None
#         self._frequency = 0
#         self._address = 0
#         self._crc_mode = 16
#         self.set_pins(self._default_pins)

#     def set_pins(self, pins):
#         # print("set_pins")
#         if self._is_open:
#             raise StateError("Pins NOT set. Device in use.")
#         else:
#             self._active_pins = pins
#             print("pins set", pins)

#     def set_spi_bus(self, bus):
#         # print("set_spi_bus")
#         if self._is_open:
#             raise StateError("SPI bus NOT set. Device in use.")
#         else:
#             if bus == 0 or bus == 1:
#                 self._spi_bus = 0
#                 print("SPI bus set", bus)
#             else:
#                 raise ValueError("Bus out of range")

#     def set_address(self, address):
#         # print("set_address")
#         if self._is_open:
#             raise StateError("Address NOT set. Device in use.")
#         else:
#             if address >= 0:
#                 if address == 0 or address & 0xffffffff:
#                     self._address = address
#                     print("Address set", address)
#                 else:
#                     raise ValueError("Address out of range")
#             else:
#                 raise ValueError("Address out of range")

#     def set_crc_mode(self, mode):
#         # print("set_crc_mode")
#         if self._is_open:
#             raise StateError("CRC mode NOT set. Device in use.")
#         else:
#             if mode == 0 or mode == 8 or mode == 16:
#                 self._crc_mode = mode
#                 print("CRC mode set", mode)
#             else:
#                 raise ValueError("CRC mode must be one of 0, 8, 16")

#     def set_frequency(self, frequency):
#         # print("set_frequency")
#         if self._is_open:
#             raise StateError("Frequency NOT set. Device in use.")
#         else:
#             # TODO Verify frequency 
#             if mode == 0 or mode == 8 or mode == 16:
#                 self._crc_mode = mode
#                 print("CRC mode set", mode)
#             else:
#                 raise ValueError("CRC mode must be one of 0, 8, 16")

#     def open(self, frequency, callback=None):
#         # print("open")
#         if self._is_open:
#             if callback:
#                 if self._is_transmitter:
#                     raise StateError("open as transmitter")
#             else:
#                 if not self._is_transmitter:
#                     raise StateError("open as receiver")
#         else:
#             if callback:
#                 print("open as receiver:", frequency, callback)
#                 self._callback = callback
#                 self._is_transmitter = False
#             else:
#                 print("open as transmitter", frequency)
#                 self._is_transmitter = True
#             self._hw_configure()
#             self._is_open = True

#     def write(self, data):
#         # print("write")
#         if self._is_open:
#             if self._is_transmitter:
#                 self._hw_write(data)
#                 print("wrote", data)
#             else:
#                 raise StateError("Device in receive mode.")
#         else:
#             raise StateError("Device not ready.  Call open() first.")

#     def _hw_configure(self):
#         """ Uses member variables directly """
#         print("_hw_configure")

#     def _hw_write(self, data):
#         print("_hw_write", data)

#     def _hw_release(self):
#         print("_hw_release")


# import Queue
# import pigpio

# class Nrf905Hardware:
#     """ Controls the nRF905 module.
    
#     The nRF905 terms are used in this module.
#     """

#     CRYSTAL_FREQUENCY_HZ = 16 * 1000 * 1000  # 16MHz is on the board I'm using.
    
#     def _init_(self):
#         print("init")
#         self._pi = pigpio.pi()
#         self._gpio = Nrf905Gpio(self._pi)
#         self._spi = Nrf905Spi(self._pi)
#         self._receive_queue = Queue.Queue()

#     def term(self):
#         print("term")
#         self._spi.term(self._pi)
#         self._gpio.term(self._pi)
#         self._pi.stop()

#     def open(self):
#         """ Set up the nRF905 module in power down mode. """
#         print("open")
#         if self._pi.connected:
#             self._gpio.set_mode(self._pi, Nrf905Gpio.POWER_DOWN)
#             self._spi.open()
#             self._receive_queue = 0  # Clear the queue. 
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
#         self._gpio.set_mode(self._pi, Nrf905Gpio.STANDBY)
#         # Write to registers
#         self._gpio.set_mode(self._pi, Nrf905Gpio.TRANSMIT)

#     def data_ready_callback(self):
#         """ When data is ready, drop out of receive mode, read the data from 
#         the SPI RX register, go back into receive mode and finally write the 
#         data to the rx queue.
#         """
#         print("drc")
#         self._gpio.set_mode_standby(self._pi)
#         data = self._spi.read_rx_data(self._pi)
#         self._gpio.set_mode_receive(self._pi)
#         for byte in data:
#             self._receive_queue.put(byte)
#         print(data)

#     def receive(self, address):
#         print("receive", address)
#         self._gpio.set_mode(self._pi, Nrf905Gpio.STANDBY)
#         self._gpio.set_data_ready_callback(self._pi, self.data_ready_callback)
#         # Send data to registers for receive.
#         self._spi.set_address(self._pi, address)
#         self._gpio.set_mode(self._pi, Nrf905Gpio.RECEIVE)

#     def get_receive_data(self):
#         """ Returns a list of all bytes in the RX queue.  If the queue is empty,
#         returns empty list.
#         """
#         result = []
#         if len(self._receive_queue) > 0:
#             while not self._receive_queue.empty():
#                 byte = self._receive_queue.get()
#                 result.append(byte)
#         return result

