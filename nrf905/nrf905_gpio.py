#!/usr/bin/env python3

import pigpio

class Nrf905Gpio:
    """ Control the GPIO pins when using the nRF905.  Pins used are:
    
        RPi                         nRF905
        Pin No.     Name            Board   Datasheet   Notes
TODO 17 and 18 are used by SPI1
        11          GPIO17          PWR     PWR_UP      0 = standby, 1 = working
        12          GPIO18          DR      DR          1 = Data ready (resistor)

        15          GPIO22          TxEN    TX_EN       0 = receive, 1 = transmit
        16          GPIO23          CD      CD          1 = Carrier detetcted (resistor)
        18          GPIO24          AM      AM          1 = Address matched (resistor)
        22          GPIO25          CE      TRX_CE      0 = disable, 1 = enable
    
        This module does not own the pigpio instance so all functions need the
        instance passed in. 

        Callbacks can be set up once and left in place.  The nRF905 only changes
        the state on these pins when in receive mode. 
    """
    
    # GPIO pins.  Uses BCM numbers same as pigpio.
    POWER_UP = 17
    TRANSMIT_ENABLE = 22
    TRANSMIT_RECEIVE_CHIP_ENABLE = 25
    output_pins = [POWER_UP, TRANSMIT_ENABLE, TRANSMIT_RECEIVE_CHIP_ENABLE]

    DATA_READY = 18
    CARRIER_DETECT = 23
    ADDRESS_MATCHED = 24
    callback_pins = [DATA_READY, CARRIER_DETECT, ADDRESS_MATCHED]

    # Modes, see nRF905 datasheet, table 11.
    POWER_DOWN = 0
    # This mode allows reading data from the RX register.
    STANDBY = 1
    # Activate receiver.
    SHOCKBURST_RX = 2
    # Activate transmitter.
    SHOCKBURST_TX = 3

    def __init__(self, pi):
        # print("__init__")
        # Output pins controlling nRF905 - set all to 0.
        for pin in self.output_pins:
            pi.set_mode(pin, pigpio.OUTPUT)
            pi.write(pin, 0)
        self.__callback_dict = dict()

    def term(self, pi):
        # print("term")
        for pin in self.callback_pins:
            self.clear_callback(pi, pin)
            self.reset_pin(pi, pin)
        for pin in self.output_pins:
            self.reset_pin(pi, pin)

    def reset_pin(self, pi, pin):
        # print("reset_pin", pin)
        # Set the given pin to input mode. 
        # GPIO0-8 default to use pull up resistor.
        # GPIO9-27 default to use pull down resistor.
        if pin >= 0 and pin <= 27:
            pi.set_mode(pin, pigpio.INPUT)
            if pin <=8:
                pi.set_pull_up_down(pin, pigpio.PUD_UP)
            else:
                pi.set_pull_up_down(pin, pigpio.PUD_DOWN)

    def set_mode_power_down(self, pi):
        pi.write(self.POWER_UP, 0)
        pi.write(self.TRANSMIT_RECEIVE_CHIP_ENABLE, 0)
        pi.write(self.TRANSMIT_ENABLE, 0)

    def set_mode_standby(self, pi):
        pi.write(self.POWER_UP, 1)
        pi.write(self.TRANSMIT_RECEIVE_CHIP_ENABLE, 0)
        pi.write(self.TRANSMIT_ENABLE, 0)

    def set_mode_receive(self, pi):
        pi.write(self.POWER_UP, 1)
        pi.write(self.TRANSMIT_RECEIVE_CHIP_ENABLE, 1)
        pi.write(self.TRANSMIT_ENABLE, 0)

    def set_mode_transmit(self, pi):
        pi.write(self.POWER_UP, 1)
        pi.write(self.TRANSMIT_RECEIVE_CHIP_ENABLE, 1)
        pi.write(self.TRANSMIT_ENABLE, 1)

    def set_callback(self, pi, pin, callback_function):
        # print("set_callback", pin)
        # Using index() causes a ValueError exception if the pin is not found.
        self.callback_pins.index(pin)
        # Set up the pin as an input.
        # PUD_OFF is used as this is what works with the nRF905 module.
        pi.set_mode(pin, pigpio.INPUT)
        pi.set_pull_up_down(pin, pigpio.PUD_OFF)
        # Create callback object and store it for use by the cancel function.
        callback_obj = pi.callback(pin, pigpio.EITHER_EDGE, callback_function)
        self.__callback_dict[pin] = callback_obj

    def clear_callback(self, pi, pin):
        """ Clears the callback for the given pin.
        Returns True if pin found.
        """
        # print("clear_callback", pin)
        result = False
        try:
            callback = self.__callback_dict[pin]
            callback.cancel()
            del self.__callback_dict[pin]
            self.reset_pin(pi, pin)
            result = True
        except KeyError:
            pass
        return result
