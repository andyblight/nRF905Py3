#!/usr/bin/env python3

import pigpio
import nrf905spi

class nrf905gpio:
    """ Control the GPIO pins when using the nRF905.  Pins used are:
    
        RPi                         nRF905
        Pin No.     Name            Board   Datasheet   Notes
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

    # nRF905 modes, see nRF905 datasheet, table 11.
    POWER_DOWN = 0
    # This mode allows reading data from the RX register.
    STANDBY = 1
    # Activate receiver.
    SHOCKBURST_RX = 2
    # Activate transmitter.
    SHOCKBURST_TX = 3

    def __init__(self, pi):
        # Output pins controlling nRF905 - set all to 0.
        r pin in self.__output_pins:
            pi.set_mode(pin, pigpio.OUTPUT)
            pi.write(pin, 0)
        # Callback pins are sorted out when each callback is set up.
        self.__active_callbacks = []
        
    def term(self, pi):
        print("reset")
        for pin in self.__callback_pins:
            self.clear_callback(pi, pin)
        r pin in self.__output_pins:
            self.reset_pin(pi, pin)

    def reset_pin(self, pi, pin):
        print("reset_in")
        # Set the given pin to input mode. 
        # GPIO0-8 have pull up resistor.
        # GPIO9-27 have pull down resistor.
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
        # Using index() causes a ValueError exception if the pin is not found.
        _ = self.__callback_pins.index(pin)
        # Set up the pin and add callback
        pi.set_mode(pin, pigpio.INPUT)
        pi.set_pull_up_down(pin, pigpio.PUD_OFF)
        callback = pi.callback(pin, pigpio.EITHER_EDGE, callback_function)
        self.__active_callbacks.append((pin, callback))

    def clear_callback(self, pi, pin):
        found = False
        for entry in self.__active_callbacks:
            if entry[0] == pin:
                entry[1].cancel()
                self.__active_callbacks.remove(entry)
                found = True
                break
        if not found:
            raise ValueError("Invalid pin", pin)
