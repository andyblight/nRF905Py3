#!/usr/bin/env python3
"""  The API for the nRF905 device.
"""

import pigpio
import time

from nrf905.nrf905_spi import Nrf905Spi
from nrf905.nrf905_gpio import Nrf905Gpio
from nrf905.nrf905_state_machine import Nrf905StateMachine
from nrf905.nrf905_config import Nrf905ConfigRegister


class Nrf905:
    """ The interface to control a nRF905 device.  This class does all the
    parameter and state checking as well as any buffering.
    The actual byte bashing is done in the modules Nrf905Gpio and Nrf905Spi.

    Example usage: see ../nrf905-example.py
    """

    def __init__(self):
        # nRF905 properties
        self._frequency_mhz = 0.0
        self._rx_address = -1
        self._tx_address = 0
        self._payload_width = 32
        # Objects to make the class work.
        self._state_machine = Nrf905StateMachine()
        self._pi = None
        self._spi = None
        self._gpio = None
        self._rx_callback = None
        # Internal properties.
        self._channel = -1  # Set from frequency.
        self._hfreq_pll = -1  # Set from frequency.
        self._open = False
        self._next = False
        self._next_tx_mode_rx = False

    @property
    def frequency(self):
        return self._frequency_mhz

    @frequency.setter
    def frequency(self, frequency_mhz, country="GBR"):
        """ Validates and sets the frequency for the device in MHz. """
        print("frequency:", frequency_mhz)
        if Nrf905ConfigRegister.is_valid(frequency_mhz, country):
            (channel, hfreq_pll) = Nrf905ConfigRegister.frequency_to_channel(
                frequency_mhz
            )
            if channel < 0:
                raise ValueError("Invalid frequency.")
            else:
                self._frequency_mhz = frequency_mhz
                self._channel = channel
                self._hfreq_pll = hfreq_pll
        else:
            raise ValueError(
                "Frequency {} not valid in {}.".format(frequency_mhz, country)
            )

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
        Please read datasheet for adivce on setting address values.
        """
        print("set_tx_address:", address)
        if address.bit_length() > 32:
            raise ValueError("Address contains more than 32 bits.")
        else:
            self._tx_address = address

    @property
    def payload_width(self):
        return self._payload_width

    @payload_width.setter
    def payload_width(self, width):
        """ Sets the payload width. Must be 32 or less.
        Uses the payload width value for transmit and receive payloads.
        Default value is 32 bytes.
        """
        print("set_payload_width:", width)
        if 1 <= width <= 32:
            raise ValueError("width must be between 1 and 32 bytes inclusive.")
        else:
            self._payload_width = width

    @property
    def next_tx_mode_rx(self):
        return self._next_tx_mode_rx

    @next_tx_mode_rx.setter
    def next_tx_mode_rx(self, next_mode):
        """ Sets the next tx mode.  True is receive mode, False is standby.
        """
        print("next_tx_mode_rx:", next_mode)
        self._next_tx_mode_rx = next_mode

    def open(self, callback):
        """ Creates the instances of Nrf905Spi and Nrf905Gpio.
        Applies previously set values to nRF905 device.
        Prepares data received callback for use.
        """
        print("open")
        if self._open:
            raise StateError("Already open.  Call close() before retrying.")
        else:
            # Frequency and RX address must be set before open is called.
            if (
                self._channel == -1
                or self._hfreq_pll == -1
                or self._rx_address == -1
            ):
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
                config.set_rx_pw(self._payload_width)
                config.set_tx_pw(self._payload_width)
                self._spi.configuration_register_write(config)
                # The TX address can be set later.
                if self._tx_address != 0:
                    self.spi.write_transmit_address(self._tx_address)
                # Setup internal callbacks for state changes.
                self._gpio.set_callback(
                    self._pi, Nrf905Gpio.DATA_READY, self._data_ready_callback
                )
                self._gpio.set_callback(
                    self._pi,
                    Nrf905Gpio.CARRIER_DETECT,
                    self._carrier_detect_callback,
                )
                self._gpio.set_callback(
                    self._pi,
                    Nrf905Gpio.ADDRESS_MATCHED,
                    self._address_matched_callback,
                )
                self._open = True

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
        self._open = False

    def send(self, payload):
        """ Sends the payload. Maximum of 32 bytes will be sent.
        """
        print("write:", payload)
        if len(payload) > self._payload_width:
            raise ValueError(
                "'payload' was longer than payload width of:",
                self._payload_width,
            )
        else:
            if not self._open:
                raise StateError("Call Nrf905.open() first.")
            else:
                self._wait_until_free()
                # Put into standby if not already.
                if self.nrf905.state != "standby":
                    self._enter_standy()
                # Load the data.
                self._spi.write_transmit_payload(payload)
                # Send the data.
                self._enter_tx_mode()
                # The next state changes are driven by the state machine
                # so exit this function.

    def _wait_until_free(self):
        """ Blocks until the transceiver is not busy.
        """
        while self._state_machine.is_busy():
            time.sleep(0.001)

    def _enter_standy(self):
        """ Set the mode and state. """
        # Delay from Arduino code.
        time.sleep(0.014)
        self._gpio.set_mode_standby(self._pi)
        self._state_machine.power_up()

    def _enter_rx_mode(self):
        """ Set the mode and state. """
        self._gpio.set_mode_receive(self._pi)
        self._state_machine.receiver_enable()

    def _enter_tx_mode(self):
        """ Set the mode and state. """
        self._gpio.set_mode_transmit(self._pi)
        self._state_machine.transmit()

    def _enter_power_down(self):
        """ Set the mode and state. """
        self._gpio.set_mode_power_down(self._pi)
        self._state_machine.power_down()

    def _carrier_detect_callback(data):
        print("cdc:", data)
        # TODO Change state

    def _address_matched_callback(data):
        print("amc:", data)
        # TODO Change state

    def _data_ready_callback(data):
        print("drc:", data)
        # TODO Change state


class StateError(Exception):
    """ Exception raised when functions are called when in the wrong state.
    Attributes:
        message -- explanation of the error
    """

    def _init_(self, message):
        self.message = message
