class Nrf905:
    """ The interface to control a nRF905 device.  This class does all the
    parameter checking and state checking.  The actual byte bashing is done in
    the module Nrf905Hardware.

    Important points to note about the nRF905.
    The device can work as a transmitter or a receiver but not both together.
    This means that the state has to be considered.
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
        self.__crc_mode = 16
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
                    self.__address = address
                    print("Address set", address)
                else:
                    raise ValueError("Address out of range")
            else:
                raise ValueError("Address out of range")

    def set_crc_mode(self, mode):
        # print("set_crc_mode")
        if self.__is_open:
            raise StateError("CRC mode NOT set. Device in use.")
        else:
            if mode == 0 or mode == 8 or mode == 16:
                self.__crc_mode = mode
                print("CRC mode set", mode)
            else:
                raise ValueError("CRC mode must be one of 0, 8, 16")

    def set_frequency(self, frequency):
        # print("set_frequency")
        if self.__is_open:
            raise StateError("Frequency NOT set. Device in use.")
        else:
            # TODO Verify frequency 
            if mode == 0 or mode == 8 or mode == 16:
                self.__crc_mode = mode
                print("CRC mode set", mode)
            else:
                raise ValueError("CRC mode must be one of 0, 8, 16")

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
            self.__hw_configure()
            self.__is_open = True

    def write(self, data):
        # print("write")
        if self.__is_open:
            if self.__is_transmitter:
                self.__hw_write(data)
                print("wrote", data)
            else:
                raise StateError("Device in receive mode.")
        else:
            raise StateError("Device not ready.  Call open() first.")

    def close(self):
        # print("close")
        self.__hw_release()
        self.__is_open = False

    def __hw_configure(self):
        """ Uses member variables directly """
        print("__hw_configure")

    def __hw_write(self, data):
        print("__hw_write", data)

    def __hw_release(self):
        print("__hw_release")


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

