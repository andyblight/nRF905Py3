#!/usr/bin/env python3
"""  The API for the nRF905 device.
"""

import logging
import pigpio
import time
import threading

from nrf905.nrf905_spi import Nrf905Spi
from nrf905.nrf905_gpio import Nrf905Gpio
from nrf905.nrf905_state_machine import Nrf905StateMachine
from nrf905.nrf905_config import Nrf905ConfigRegister

# Set up logging.
logger = logging.getLogger("Nrf905")
logger.setLevel(logging.DEBUG)


class Nrf905:
    """ The interface to control a nRF905 device.  This class does all the
    parameter and state checking as well as any buffering.
    The actual byte bashing is done in the modules Nrf905Gpio and Nrf905Spi.

    Example usage: see ../nrf905-example.py
    """

    _READ_SLEEP_S = 0.01  # 10ms
    _SEND_SLEEP_S = 0.001  # 1ms Want this to be quick.
    _NEXT_MODE_SLEEP_S = 0.0007  # 700us from datasheet.
    _POWER_UP_SLEEP_S =  0.003  # 3ms Powering up takes longer.

    def __init__(self):
        # nRF905 properties
        self._frequency_mhz = 0.0
        self._rx_address = -1
        self._tx_address = 0
        self._payload_width = 32
        self._channel = -1  # Set from frequency.
        self._hfreq_pll = -1  # Set from frequency.
        self._tx_power = 0b00
        # Objects to make the class work.
        self._state_machine = Nrf905StateMachine()
        self._pi = None
        self._spi = None
        self._gpio = None
        self._read_thread = None
        self._receive_callback = None
        # Internal variables.
        self._open = False
        self._next = False
        self._next_tx_mode_rx = False
        self._carrier_busy = False
        self._auto_receive = False
        self._data_sent = False
        self._data_received = False
        # Logging test
        logger.critical("critical")
        logger.error("error")
        logger.warning("warning")
        logger.info("info")
        logger.debug("debug")

    @property
    def frequency_mhz(self):
        return self._frequency_mhz

    @frequency_mhz.setter
    def frequency_mhz(self, frequency_mhz, country="GBR"):
        """ Validates and sets the frequency for the device in MHz. """
        logger.debug("frequency: {}".format(frequency_mhz))
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
        logger.debug("rx_address: {}".format(hex(address)))
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
        logger.debug("set_tx_address: {}".format(hex(address)))
        if address.bit_length() > 32:
            raise ValueError("Address contains more than 32 bits.")
        else:
            self._tx_address = address

    @property
    def transmit_power_db(self):
        return self._tx_power

    @transmit_power_db.setter
    def transmit_power(self, power):
        """ Sets the transmit power in dB.
        Values will be rounded down to one of these values: -10, -2, +6, +10.
        """
        logger.debug("transmit_power_db: {}".format(power))
        if power <= -10:
            self._tx_power = 0b00
        elif power <= -2:
            self._tx_power = 0b01
        elif power <= 6:
            self._tx_power = 0b10
        else:
            self._tx_power = 0b11

    @property
    def payload_width(self):
        return self._payload_width

    @payload_width.setter
    def payload_width(self, width):
        """ Sets the payload width. Must be 32 or less.
        Uses the payload width value for transmit and receive payloads.
        Default value is 32 bytes.
        """
        logger.debug("set_payload_width: {}".format(width))
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
        logger.debug("next_tx_mode_rx:", next_mode)
        self._next_tx_mode_rx = next_mode

    def enable_receive(self, callback):
        """ Prepares data received callback for use.
        Enables automatic transition to receive mode after every send.
        The callback function should return nothing and take one string
        (the payload). Callback is on a separate thread.
        """
        if self._open:
            raise StateError(
                "Cannot change when open.  Call close() before retrying."
            )
        else:
            self._auto_receive = True
            self._receive_callback = callback
            # Start receive thread.
            self._read_thread = threading.Thread(target=self._read_payload)
            self._read_thread.start()

    def open(self):
        """ Creates the instances of Nrf905Spi and Nrf905Gpio.
        Applies previously set values to nRF905 device.
        """
        logger.debug("open")
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
                # Set tx power
                config.set_pa_pwr(self._tx_power)
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
        logger.debug("close")
        self._open = False
        self._enter_power_down()
        if self._auto_receive:
            self._read_thread.join()
        # Release objects.
        self._spi.close()
        self._pi.stop()

    def send(self, data):
        """ Sends the data. Maximum of 32 bytes will be sent (checked by
        Nrf905Spi.write_transmit_payload()).
        NOTE: data must be a bytearray.
        """
        logger.debug("send:", data)
        if not self._open:
            raise StateError("Call Nrf905.open() first.")
        else:
            # Block until the transceiver is not busy.
            while self._state_machine.is_busy():
                time.sleep(self._SEND_SLEEP_S)
            # Put into standby.
            self._enter_standby()
            # Load the data.
            payload = bytearray()
            payload.extend(data)
            self._spi.write_transmit_payload(payload)
            # Tell the device to send the data and block until done.
            self._data_sent = False
            self._enter_tx_mode()
            while not self._data_sent:
                time.sleep(self._SEND_SLEEP_S)
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

    def _read_payload(self):
        """ This function is run on a thread. """
        logger.debug("rp")
        self._data_received = False
        # Wait until open.
        while not self._open:
            time.sleep(self._READ_SLEEP_S)
        # Loop until driver closed.
        while self._open:
            logger.debug("rp: waiting...")
            # Wait for data to be received.
            while not self._data_received:
                if not self._open:
                    break
                time.sleep(self._READ_SLEEP_S)
            logger.debug("/nrp: received")
            # When the payload has been read, the DR pin will go low
            # causing a state change.
            payload = self._spi.read_receive_payload()
            # Call the callback. payload is a bytearray.
            self._receive_callback(payload)
            self._data_received = False

    def _enter_power_down(self):
        """ Set the mode and state. """
        logger.debug("epd")
        self._gpio.set_mode_power_down(self._pi)
        time.sleep(self._NEXT_MODE_SLEEP_S)
        self._state_machine.power_down()

    def _enter_standby(self):
        """ Set the mode and state. """
        logger.debug("es")
        if self._state_machine.state != "standby":
            self._gpio.set_mode_standby(self._pi)
            time.sleep(self._NEXT_MODE_SLEEP_S)
            if self._state_machine.state == "sleep":
                self._state_machine.power_up()
            elif self._state_machine.state == "receiving_listening":
                self._state_machine.receiver_disable()

    def _enter_rx_mode(self):
        """ Set the mode and state. """
        logger.debug("erm")
        self._gpio.set_mode_receive(self._pi)
        time.sleep(self._NEXT_MODE_SLEEP_S)
        self._state_machine.receiver_enable()

    def _enter_tx_mode(self):
        """ Set the mode and state. """
        logger.debug("etm: {}".format(self._carrier_busy))
        self._gpio.set_mode_transmit(self._pi)
        time.sleep(self._NEXT_MODE_SLEEP_S)
        # If carrier not present, start transmitting now else wait.
        if not self._carrier_busy:
            self._state_machine.transmit_now()
        else:
            self._state_machine.transmit_wait()

    def _carrier_detect_callback(self, gpio, level, tick):
        """ Only used for transmitting. """
        logger.debug("cdc: {}, {}, {}".format(gpio, level, tick))
        if level == 0:
            # High to low
            self._carrier_busy = False
            # If waiting to start transmitting, start transmitting.
            if self._state_machine.state == "transmitting_waiting":
                self._state_machine.no_carrier()
        elif level == 1:
            # Low to high.
            self._carrier_busy = True
        else:
            logger.error("Watchdog!")

    def _address_matched_callback(self, gpio, level, tick):
        """ Update state machine directly. """
        logger.debug("amc: {}, {}, {}".format(gpio, level, tick))
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
            logger.error("Watchdog!")

    def _data_ready_callback(self, gpio, level, tick):
        """ Update state machine directly. """
        logger.debug("drc: {}, {}, {}".format(gpio, level, tick))
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
                self._data_received = True
        else:
            logger.error("Watchdog!")


class StateError(Exception):
    """ Exception raised when functions are called when in the wrong state.
    Attributes:
        message -- explanation of the error
    """

    def _init_(self, message):
        self.message = message
