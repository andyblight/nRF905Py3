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
        self._carrier_busy = False
        self._auto_receive = False
        self._data_sent = False

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
        print("rx_address:", hex(address))
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
        print("set_tx_address:", hex(address))
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

    def enable_receive(self, callback):
        """ Prepares data received callback for use.
        Enabled automatic tranistion to receive mode after every transmission.
        """
        if self._open:
            raise StateError(
                "Cannot change when open.  Call close() before retrying."
            )
        else:
            self._auto_receive = True
            print("TODO callback")
            # Callback processed on separate thread?

    def open(self):
        """ Creates the instances of Nrf905Spi and Nrf905Gpio.
        Applies previously set values to nRF905 device.
        """
        # print("open")
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
                # Start off in standby mode.
                self._enter_standby()
                # Config register.
                config = Nrf905ConfigRegister()
                config.board_defaults()
                # Set frequency
                config.set_channel_number(self._channel)
                config.set_hfreq_pll(self._hfreq_pll)
                # Receive address
                config.set_rx_address(self._rx_address)
                # Payload widths
                config.set_rx_pw(self._payload_width)
                config.set_tx_pw(self._payload_width)
                # 16 bit CRC enabled
                config.set_crc_mode(1)
                config.set_crc_en(1)
                # 16MHz clock speed
                config.set_xof_mhz(16)
                # Disable output clock.
                config.set_up_clk_en(0)
                self._spi.configuration_register_write(config)
                # The TX address can be set later.
                if self._tx_address != 0:
                    self._spi.write_transmit_address(self._tx_address)
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
                self._print_startup_info()
                if self._auto_receive:
                    self._enter_rx_mode()

    def close(self):
        """ Releases the instances of Nrf905Spi and Nrf905Gpio.
        The nRF905 device is left in the state last used.
        """
        # print("close")
        self._enter_power_down()
        # Release objects.
        self._spi.close()
        self._pi.stop()
        self._open = False

    def send(self, payload):
        """ Sends the payload. Maximum of 32 bytes will be sent (checked by
        Nrf905Spi.write_transmit_payload()).
        """
        print("send:", payload)
        if not self._open:
            raise StateError("Call Nrf905.open() first.")
        else:
            # Block until the transceiver is not busy.
            while self._state_machine.is_busy():
                time.sleep(0.001)
            # Put into standby.
            self._enter_standby()
            # Load the data.
            self._spi.write_transmit_payload(payload)
            # Tell the device to send the data and block until done.
            self._data_sent = False
            self._enter_tx_mode()
            while not self._data_sent:
                time.sleep(0.001)
            # Put into next mode.
            self._enter_standby()
            if self._auto_receive:
                self._enter_rx_mode()

    def _print_startup_info(self):
        """ Print out frequency and address. """
        # Read tx address (proves SPI is working correctly).
        tx_address = self._spi.read_transmit_address()
        print("----- Started -----")
        print("Frequency", self._frequency_mhz, "MHz")
        print("Transmit address", hex(tx_address))
        if self._auto_receive:
            print("Receive address", hex(self._rx_address))
        else:
            print("Transmit only.")
        print("-------------------")

    def _enter_power_down(self):
        """ Set the mode and state. """
        print("epd")
        self._gpio.set_mode_power_down(self._pi)
        time.sleep(0.001)
        self._state_machine.power_down()

    def _enter_standby(self):
        """ Set the mode and state. """
        print("es")
        if self._state_machine.state != "standby":
            self._gpio.set_mode_standby(self._pi)
            # Delay from Arduino code.
            time.sleep(0.014)
            if self._state_machine.state == "sleep":
                self._state_machine.power_up()
            elif self._state_machine.state == "receiving_listening":
                self._state_machine.receiver_disable()

    def _enter_rx_mode(self):
        """ Set the mode and state. """
        print("erm")
        self._gpio.set_mode_receive(self._pi)
        time.sleep(0.001)
        self._state_machine.receiver_enable()

    def _enter_tx_mode(self):
        """ Set the mode and state. """
        print("etm: carrier:", self._carrier_busy)
        self._gpio.set_mode_transmit(self._pi)
        time.sleep(0.001)
        self._state_machine.transmit()
        # If carrier not present, start transmitting.
        if not self._carrier_busy:
            self._state_machine.no_carrier()

    def _carrier_detect_callback(self, gpio, level, tick):
        """ Only used for transmitting. """
        print("cdc:", gpio, level, tick)
        if level == 0:
            # High to low
            self._carrier_busy = False
            # If waiting to start transmitting, start transmitting.
            if self._state_machine.is_transmitting_waiting():
                self._state_machine.no_carrier()
        elif level == 1:
            # Low to high.
            self._carrier_busy = True
        else:
            print("Watchdog!")

    def _address_matched_callback(self, gpio, level, tick):
        """ Update state machine directly. """
        print("amc:", gpio, level, tick)
        if level == 0:
            # High to low
            # CRC failed so go back to listening.
            if self._state_machine.is_receiving_receiving_data():
                self._state_machine.bad_crc()
        elif level == 1:
            # Address matches so move to next state.
            if self._state_machine.is_receiving_listening():
                self._state_machine.address_match()
        else:
            print("Watchdog!")

    def _data_ready_callback(self, gpio, level, tick):
        """ Update state machine directly. """
        print("drc:", gpio, level, tick)
        if level == 0:
            # High to low
            if self._state_machine.is_receiving_received():
                # This happens when the data has been read from the
                # payload registers.
                self._state_machine.received2listening()
        elif level == 1:
            if self._state_machine.is_transmitting_sending():
                # Transmit has completed.
                self._state_machine.data_ready_tx()
                self._data_sent = True
            elif self._state_machine.is_receiving_receiving_data():
                # Successful receive with good CRC (if enabled).
                self._state_machine.data_ready_rx()
        else:
            print("Watchdog!")


class StateError(Exception):
    """ Exception raised when functions are called when in the wrong state.
    Attributes:
        message -- explanation of the error
    """

    def _init_(self, message):
        self.message = message
