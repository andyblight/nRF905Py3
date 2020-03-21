#!/usr/bin/env python3

import pigpio
import queue
import threading

from nrf905.nrf905_spi import Nrf905Spi
from nrf905.nrf905_gpio import Nrf905Gpio
from nrf905.nrf905_state_machine import Nrf905StateMachine


# TODO Sort out callbacks.
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

    Example usage: see ../nrf905-monitor.py
    """

    def __init__(self):
        # nRF905 properties
        self._frequency_mhz = 0.0
        self._rx_address = -1
        self._tx_address = 0
        # Objects to make the class work.
        self._state_machine = Nrf905StateMachine()
        self._pi = None
        self._spi = None
        self._gpio = None
        self._rx_callback = None
        self._queue = None
        self._thread = None
        # Internal properties.
        self._channel = -1  # Set from frequency.
        self._hfreq_pll = -1  # Set from frequency.

    @property
    def frequency(self):
        return self._frequency_mhz

    @frequency.setter
    def frequency(self, frequency_mhz, country="GBR"):
        """ Validates and sets the frequency for the device in MHz. """
        print("frequency:", frequency_mhz)
        if Nrf905ConfigRegister.is_valid(frequency_mhz, country):
            (channel, hfreq_pll) = Nrf905ConfigRegister.frequency_to_channel(frequency_mhz)
            if channel < 0:
                raise ValueError("Invalid frequency.")
            else:
                self._frequency_mhz = frequency_mhz
                self._channel = channel
                self._hfreq_pll = hfreq_pll
        else:
            raise ValueError("Frequency {} not valid in {}.".format(
                frequency_mhz, country))

    @property
    def receive_address(self):
        return self._rx_address

    @receive_address.setter
    def receive_address(self, address):
        """ Sets the receive address. Must be 4 bytes or less.
        Please read datasheet for adivce on setting addres values.
        """
        print("rx_address:", address)
        if address.bit_length() > 32:
            raise ValueError("Address contains more than 32 bits.")
        else:
            self._rx_address = address

    @property
    def transmit_address(self):
        return self._tx_address

    @transmit_address.setter
    def transmit_address(self, address):
        """ Sets the transmit address. Must be 4 bytes or less.
        Please read datasheet for adivce on setting addres values.
        """
        print("set_tx_address:", address)
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
        if self._thread():
            raise StateError("Already open.  Call close() before retrying.")
        else:
            # Frequency and RX address must be set before open is called.
            if self._channel == -1 or self._hfreq_pll == -1 or \
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
                self._state_machine.power_down()
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
                self._gpio.set_callback(
                    self._pi, Nrf905Gpio.DATA_READY, data_ready_callback)
                self._gpio.set_callback(
                    self._pi, Nrf905Gpio.CARRIER_DETECT,
                    carrier_detect_callback)
                self._gpio.set_callback(
                    self._pi, Nrf905Gpio.ADDRESS_MATCHED,
                    address_matched_callback)
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

    def write(self, data):
        """ Posts the data to the transmit queue in 32 byte packets.
        Each packet in the queue will be transmitted until the queue is empty.
        """
        print("write:", data)
        if not self._thread:
            raise StateError("Call Nrf905.open() first.")
        else:
            while data:  # Contains something.
                packet = data[0:32]  # Split in to 32 byte patckets.
                self._queue.put(packet)

    def _worker(self):
        """ Wait for a packet. When a packet is available, send the packet and
        repeat.
        """
        while True:
            # Wait until transceiver is free before sending.
            with cv_busy:
                while self._state_machine.is_busy():
                    cv_busy.wait()
            data = self._queue.get()
            if data is None:
                break
            self._send(data)
            self._queue.task_done()

    def _wait_until_free(self):
        """ Blocks until the transciever is not busy. """
        # TODO
        # with cv_busy:
        #    while
        pass

    def _send(self, data):
        """ Sends a packet of data.
        """
        # TODO Change modes.
        # Write the payload data to the registers.
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
