#!/usr/bin/env python3

""" This file was created so that I could understand how the GPIO pins and 
the SPI bus could be controlled using the pigpio library.

        RPi                             nRF905
        Name            Pin No.         Name

        VCC             15              VCC
        GND             23              GND
    SPI
        GPIO27/CE       13              CE
        GPIO10/MOSI     17              MOSI
        GPIO9/MISO      19              MISO
        GPIO11/SCK      21              SCK

    Other GPIO pins
        GPIO17          11              PWR     0 = standby, 1 = working
        GPIO18          12              DR via resistor
        GPIO8           22              CSN


"""

import sys
import time
import pigpio


def test_gpios(count):
    """ Flashes the LEDs in sequence count times. """
    print("test_gpios")
    pi.write(17, 0)
    pi.write(18, 0)
    pi.write(8, 0)
    time.sleep(1)
    pi.write(17, 1)
    pi.write(18, 1)
    pi.write(8, 1)
    time.sleep(1)

def test_spi():
    print("test_spi")

# Connect to pigpoid
pi = pigpio.pi()

if not pi.connected:
   exit()

test_gpios(10)
test_spi()

# Disconnect from pigpoid
pi.stop()
