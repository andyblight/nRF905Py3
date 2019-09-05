#!/usr/bin/env python3

import Queue
import pigpio
from nrf905.nrf905_spi import Nrf905Spi
from nrf905.nrf905_gpio import Nrf905Gpio

class Nrf905Hardware:
    """ Controls the nRF905 module.
    
    The nRF905 terms are used in this module.
    """

    CRYSTAL_FREQUENCY_HZ = 16 * 1000 * 1000  # 16MHz is on the board I'm using.
    
    def __init__(self):
        print("init")
        self.__pi = pigpio.pi()
        self.__gpio = Nrf905Gpio(self.__pi)
        self.__spi = Nrf905Spi(self.__pi)
        self.__receive_queue = Queue.Queue()

    def term(self):
        print("term")
        self.__spi.term(self.__pi)
        self.__gpio.term(self.__pi)
        self.__pi.stop()

    def open(self):
        """ Set up the nRF905 module in power down mode. """
        print("open")
        if self.__pi.connected:
            self.__gpio.set_mode(self.__pi, Nrf905Gpio.POWER_DOWN)
            self.__spi.open()
            self.__receive_queue = 0  # Clear the queue. 
        else:
            raise ProcessLookupError("Could not connect to pigpio daemon.")

    def transmit(self, data):
        """ Put into standby mode, write the data to be transmitted to the 
        nRF905 and set mode to transmit.
        If the data given is too bit to be transmitted in one burst, the data
        is split into burst sized chunks and transmitted until all the data has
        been sent.
        """
        print("transmit", data)
        self.__gpio.set_mode(self.__pi, Nrf905Gpio.STANDBY)
        # Write to registers
        self.__gpio.set_mode(self.__pi, Nrf905Gpio.TRANSMIT)

    def data_ready_callback(self):
        """ When data is ready, drop out of receive mode, read the data from 
        the SPI RX register, go back into receive mode and finally write the 
        data to the rx queue.
        """
        print("drc")
        self.__gpio.set_mode_standby(self.__pi)
        data = self.__spi.read_rx_data(self.__pi)
        self.__gpio.set_mode_receive(self.__pi)
        for byte in data:
            self.__receive_queue.put(byte)
        print(data)

    def receive(self, address):
        print("receive", address)
        self.__gpio.set_mode(self.__pi, Nrf905Gpio.STANDBY)
        self.__gpio.set_data_ready_callback(self.__pi, self.data_ready_callback)
        # Send data to registers for receive.
        self.__spi.set_address(self.__pi, address)
        self.__gpio.set_mode(self.__pi, Nrf905Gpio.RECEIVE)

    def get_receive_data(self):
        """ Returns a list of all bytes in the RX queue.  If the queue is empty,
        returns empty list.
        """
        result = []
        if len(self.__receive_queue) > 0:
            while not self.__receive_queue.empty():
                byte = self.__receive_queue.get()
                result.append(byte)
        return result

