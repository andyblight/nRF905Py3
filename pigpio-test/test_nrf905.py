#!/usr/bin/env python3

""" This file was created so that I could understand how to make the nRF905 SPI registers work.
"""

import sys
import time
import pigpio


def reset_gpios(pi):
    gpios = []
    for pin in gpios:
        pi.set_mode(pin, pigpio.INPUT)


def set_csn(pi, state):
    CSN = 8
    pi.set_mode(CSN, pigpio.OUTPUT)
    pi.write(CSN, state)


def test_spi(pi):
    # Set CSN high (not selected)
    set_csn(pi, 1)
    # Can only use channel 0 on model B.
    spi_channel = 0
    # Baud in range 32k to 125M.  50k seems like a good speed to start with.
    baud = 50 * 1000
    # nRF905 support SPI mode 0.
    spi_flags = 0
    # Open SPI device
    spi_h = pi.spi_open(spi_channel, baud, spi_flags)
    # Prepare command.
    command = bytearray()
    # INSTRUCTION_R_TX_ADDRESS = 0b00100011
    command.append(0b00100011)
    print("Read transmit address command", command.hex())
    # Set CSN low (selected)
    set_csn(pi, 0)
    # Transfer the data
    (count, data) = pi.spi_xfer(spi_h, command)
    # Set CSN high (not selected)
    set_csn(pi, 1)
    # Print what we received
    print(count, data.hex())
    # Close the spi bus
    pi.spi_close(spi_h)


#### START HERE ####
print("Tests started")

# Connect to pigpoid
pi = pigpio.pi()

if pi.connected:
    reset_gpios(pi)
    test_spi(pi)
    print("Tests finished.")
    reset_gpios(pi)
    # Disconnect from pigpoid
    pi.stop()

