#!/usr/bin/env python3

""" This file was created so that I could understand how the GPIO pins and
the SPI bus could be controlled using the pigpio library.

        RPi                             nRF905
        Name            Pin No.         Name

        VCC             15              VCC
        GND             23              GND

    SPI
        GPIO7/CE1       26
        GPIO8/CE0       24              CE
        GPIO9/MISO      19              MISO
        GPIO10/MOSI     17              MOSI
        GPIO11/SCK      21              SCK

    Other GPIO pins
        GPIO17          11              PWR     0 = standby, 1 = working
        GPIO18          12              DR via resistor
        GPIO25          22              CSN
"""

import sys
import time
import pigpio


def test_gpios():
    """ Flashes the any connected LEDs. """
    print("test_gpios")
    pi.set_mode(17, pigpio.OUTPUT)
    pi.set_mode(25, pigpio.OUTPUT)
    gpios = [17, 25]
    for gpio in gpios:
        pi.write(gpio, 0)
    time.sleep(0.1)
    for gpio in gpios:
        pi.write(gpio, 1)
        time.sleep(0.5)
    for gpio in gpios:
        pi.write(gpio, 0)
        time.sleep(0.5)

def test_spi():
    print("test_spi")
    # From http://abyz.me.uk/rpi/pigpio/python.html#spi_open
    # Can only use channel 0 on model B.
    spi_channel = 0
    # Baud in range 32k to 125M.  50k seems like a good speed to start with.
    baud = 50 * 1000
    # nRF905 support SPI mode 0.
    spi_flags = 0
    # Open SPI device
    spi_h = pi.spi_open(spi_channel, baud, spi_flags)
    # Transfer some data
    data_read = pi.spi_xfer(spi_h, "Hello!")
    print(data_read)
    # Close the spi bus
    pi.spi_close(spi_h)


def test_read():
    print("test_read. Polling GPIO18...")
    # Set GPIO18 as input with pull down resistor.
    gpio = 18
    pi.set_mode(gpio, pigpio.INPUT)
    pi.set_pull_up_down(gpio, pigpio.PUD_DOWN)
    for _ in range(1, 10):
        level = pi.read(gpio)
        print(level)
        time.sleep(1)


def callbackf(num, level, tick):
    print("GPIO", num, level, tick)


def test_callback():
    print("test_gpio_read. Waiting for GPIO18 to go high...")
    # Set GPIO18 as input with pull down resistor.
    gpio = 18
    pi.set_mode(gpio, pigpio.INPUT)
    pi.set_pull_up_down(gpio, pigpio.PUD_OFF)
    cb1 = pi.callback(gpio, pigpio.EITHER_EDGE, callbackf)
    time.sleep(10)
    cb1.cancel() # To cancel callback cb1.


#### START HERE ####
# Connect to pigpoid
pi = pigpio.pi()

if pi.connected:
    test_gpios()
    test_spi()
    test_read()
    test_callback()
    print("Tests finished.")
    # Disconnect from pigpoid
    pi.stop()
