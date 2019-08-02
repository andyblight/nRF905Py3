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
        22          GPIO25          CE      TRX_CE      0 = disable, 1 = enable
    
        This module does not own the pigpio instance so all functions need the
        instance passed in. 
    """
    
    # GPIO pins.  Uses BCM numbers same as pigpio.
    POWER_UP = 17
    DATA_READY = 18
    TRANSMIT_ENABLE = 22
    TRANSMIT_RECEIVE_CHIP_ENABLE = 25

    # nRF905 modes, see nRF905 datasheet, table 11.
    POWER_DOWN = 0
    # This mode allows reading data from the RX register.
    STANDBY = 1
    # Activate receiver.
    SHOCKBURST_RX = 2
    # Activate transmitter.
    SHOCKBURST_TX = 3

    def __init__(self, pi):
        self.__pins_used = [self.POWER_UP, self.DATA_READY,
                            self.TRANSMIT_ENABLE,
                            self.TRANSMIT_RECEIVE_CHIP_ENABLE]
        # Output pins controlling nRF905 - set all to 0.
        pi.set_mode(self.POWER_UP, pigpio.OUTPUT)
        pi.write(self.POWER_UP, 0)
        pi.set_mode(self.TRANSMIT_ENABLE, pigpio.OUTPUT)
        pi.write(self.TRANSMIT_ENABLE, 0)
        pi.set_mode(self.TRANSMIT_RECEIVE_CHIP_ENABLE, pigpio.OUTPUT)
        pi.write(self.TRANSMIT_RECEIVE_CHIP_ENABLE, 0)
        # DR is sorted out when the callback is set up.
        
    def term(self, pi):
        print("reset")
        self.__drcb.cancel()
        for pin in self.__pins_used:
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
        self.__drcb.cancel()

    def set_mode_standby(self, pi):
        pi.write(self.POWER_UP, 1)
        pi.write(self.TRANSMIT_RECEIVE_CHIP_ENABLE, 1)
        pi.write(self.TRANSMIT_ENABLE, 0)
        self.__drcb.cancel()

    def set_mode_receive(self, pi):
        pi.write(self.POWER_UP, 1)
        pi.write(self.TRANSMIT_RECEIVE_CHIP_ENABLE, 1)
        pi.write(self.TRANSMIT_ENABLE, 0)

    def set_mode_transmit(self, pi):
        pi.write(self.POWER_UP, 1)
        pi.write(self.TRANSMIT_RECEIVE_CHIP_ENABLE, 1)
        pi.write(self.TRANSMIT_ENABLE, 1)
        self.__drcb.cancel()

    def set_data_ready_callback(self, pi, callback):
        print("sdrc")
        gpio = self.DATA_READY 
        pi.set_mode(gpio, pigpio.INPUT)
        pi.set_pull_up_down(gpio, pigpio.PUD_OFF)
        # DR goes high when data is available.
        self.__drcb = pi.callback(gpio, pigpio.RISING_EDGE, callback)
