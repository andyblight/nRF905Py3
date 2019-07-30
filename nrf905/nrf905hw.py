#!/usr/bin/env python3

import pigpio
import nrf905spi

class nrf905hw:
    """ A wrapper class around pigpio that drives an nRF905 device.
    
    TODO Move this to the README?
    
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
        Pin No.     Name            Board   Datasheet   Notes
        11          GPIO17          PWR     PWR_UP      0 = standby, 1 = working
        12          GPIO18          DR      DR          1 = Data ready
        15          GPIO22          TxEN    TX_EN       0 = receive, 1 = transmit
        17          3V3             VCC     VDD         Max. 3.6V
        19          GPIO10/MOSI     MOSI    MOSI        SPI input
        21          GPIO9/MISO      MISO    MISO        SPI output
        22          GPIO25          CE      TRX_CE      0 = disable, 1 = enable
        23          GPIO11/SCK      SCK     SCK         SPI clock
        24          GPIO8/CE0       CSN     CSN         SPI enable, active low
        25          GND             GND

    Design considerations
    As this is a driver, it should never get out of step with the device.  This
    means checking values on the device by reading where possible and if not,
    do extra writes to ensure that values in the driver match those on the 
    device.
    
    """

    CRYSTAL_FREQUENCY_HZ = 16 * 1000 * 1000  # 16MHz is on the board I'm using.
    
    # GPIO PINS - Hardcoded for now.  Uses BCM numbers same as pigpio.
    POWER_UP = 17
    DATA_READY = 18
    TRANSMIT_ENABLE = 22
    CHIP_ENABLE = 25

    # SPI pins are defaults for pigpio bus 0 (RPi 1 A&B only have SPI bus 0).
    SPI_BUS = 0
    SPI_SCK_HZ = 1 * 1000 * 1000  # 10MHz max. (data sheet)

    def __init__(self):
        self.__pi = 0
        self.__spi_handle = 0

    def open(self):
        print("open")
        self.__pi = pigpio.pi()
        if self.__pi.connected:
            self.__spi_open()
            self.__gpio_open()
        else:
            raise ProcessLookupError("Could not connect to pigpio daemon.")

    def write(self, data):
        print("write", data)

    def release(self):
        print("release")
        self.__pi.stop()

    def __gpio_open(self):
        

    def __gpio_close(self):
        


