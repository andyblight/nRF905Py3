#!/usr/bin/env python3

# import pigpio

class nrf905:
    """ A wrapper class around pigpio that drives an nRF905 device. 
        Looking at the top (the side with the antenna sticking up) the nRF905 
        module pin out is:

        VCC         TxEN      
        CE          PWR
        CLK         CD
        AM          DR            CHIP          ANTENNA 
        MISO        MOSI
        SCK         CSN
        GND         GND

        The RPi is connected to SPI0 and some GPIO pins as follows:

        RPi                         nRF905
        Name        Pin No.         Name

        GPIO17      11              PWR     0 = standby, 1 = working
        GPIO18      12              DR via resistor
        GPIO27      13              CE
        VCC         15              VCC
        GPIO10      17              MOSI
        GPIO9       19              MISO
        GPIO11      21              SCK
        GPIO8       22              CSN
        GND         23              GND

    Important points to note about the nRF905.
    1.  The device can work as a transmitter or a receiver but not both together.
        This means that open() has to be aware if transmission is needed.
    """

    def __init__(self):
        self.__is_open = False
        self.__is_transmitter = False
        self.__default_pins = []
        self.__active_pins = []
        self.__spi_bus = 0  # Default to 0
        self.__callback = None
        self.__frequency = 0
        self.__address = 0
        self.set_pins(self.__default_pins)

    def set_pins(self, pins):
        # print("set_pins")
        if self.__is_open:
            raise StateError("Pins NOT set. Device in use.")
        else:
            self.__active_pins = pins
            print("pins set", pins)

    def set_spi_bus(self, bus):
        # print("set_spi_bus")
        if self.__is_open:
            raise StateError("SPI bus NOT set. Device in use.")
        else:
            if bus == 0 or bus == 1:
                self.__spi_bus = 0
                print("SPI bus set", bus)
            else:
                raise ValueError("Bus out of range")

    def set_address(self, address):
        # print("set_address")
        if self.__is_open:
            raise StateError("Address NOT set. Device in use.")
        else:
            if address >= 0:
                if address == 0 or address & 0xffffffff:
                    self.__address = 0
                    print("Address set", address)
                else:
                    raise ValueError("Address out of range")
            else:
                raise ValueError("Address out of range")

    def open(self, frequency, callback=None):
        # print("open")
        if self.__is_open:
            if callback:
                if self.__is_transmitter:
                    raise StateError("open as transmitter")
            else:
                if not self.__is_transmitter:
                    raise StateError("open as receiver")
        else:
            if callback:
                print("open as receiver:", frequency, callback)
                self.__callback = callback
                self.__is_transmitter = False
            else:
                print("open as transmitter", frequency)
                self.__is_transmitter = True
            self.__configure_hw()
            self.__is_open = True

    def write(self, data):
        # print("write")
        if self.__is_open:
            if self.__is_transmitter:
                print("wrote", data)
            else:
                raise StateError("Device in receive mode.")
        else:
            raise StateError("Device not ready.  Call open() first.")

    def close(self):
        # print("close")
        self.__release_hw()
        self.__is_open = False

    def __configure_hw(self):
        print("__configure_hw")

    def __release_hw(self):
        print("__release_hw")


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class StateError(Error):
    """ Exception raised when functions are called when in the wrong state.

    Attributes:
        message -- explanation of the error
    """    
    def __init__(self, message):
        self.message = message

