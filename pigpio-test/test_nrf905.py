#!/usr/bin/env python3

""" This file was created so that I could understand how to make the nRF905 SPI registers work.
NOTES:
The pigpio SPI driver controls all the SPI pins including the chip enable lines.
This means RPi GPIO pins 7, 8, 9, 10, 11 should not be used by this code.
"""

import sys
import time
import pigpio


def reset_gpios(pi):
    print("reset_gpios")
    gpios = [2, 3, 4, 14, 15, 17, 18, 22, 23, 24, 25, 27]
    for pin in gpios:
        pi.set_mode(pin, pigpio.INPUT)
    time.sleep(0.1)

def set_gpio(pi, pin, state):
    print("set_gpio", pin, state)
    pi.set_mode(pin, pigpio.OUTPUT)
    pi.write(pin, state)
    time.sleep(0.1)

def set_pwr_up(pi, state):
    PWR_UP = 22
    set_gpio(pi, PWR_UP, state)

def set_tx_ce(pi, state):
    TX_CE = 27
    set_gpio(pi, TX_CE, state)

def set_tx_en(pi, state):
    TX_EN = 15
    set_gpio(pi, TX_EN, state)

def command_read_config(pii, spi_h):
    # Command to read all 10 bytes
    read_config_command = bytearray()
    read_config_command.append(0b00100000)
    for _ in range(1, 10):
        read_config_command.append(0)
    send_command(pi, spi_h, read_config_command)

def send_command(pi, spi_h, b_command):
    print("Command is 0x", b_command.hex())
    # Transfer the data
    #pi.spi_write(spi_h, b_command)
    count, data = pi.spi_xfer(spi_h, b_command)
    # Print what we received
    print("Received", count, data)
    if count > 0:
        status_register = data.pop(0)
        print("Status 0x", status_register)
        print("Data bytes", len(data), "0x", data.hex())
    else:
        print("Received ", count, "0x", data.hex())

def test_spi(pi):
    # Can only use channel 0 on model B.
    channel = 0
    # Baud in range 32k to 125M. nRF905 is 10M.
    # Works in range 32k to 10M.
    baud = 1 * 1000 * 1000
    # nRF905 supports SPI mode 1 only.  This is not supported on SPI bus 1.
    flags = 1
    set_tx_ce(pi, 1)
    # Here to CSN beeing set to 0 takes about 100ms.
    # Open SPI device
    spi_h = pi.spi_open(channel, baud, flags)
    # Send commands
    command_read_config(pi, spi_h)
    # Close the spi bus
    # CSN high to tx_ce lo takes about 27ms.
    pi.spi_close(spi_h)
    set_tx_ce(pi, 0)


#### START HERE ####
print("Tests started")

# Connect to pigpoid
pi = pigpio.pi()

if pi.connected:
    reset_gpios(pi)
    set_pwr_up(pi, 0)
    set_tx_en(pi, 0)
    set_tx_ce(pi, 0)
    test_spi(pi)
    print("Tests finished.")
    set_pwr_up(pi, 0)
    reset_gpios(pi)
    # Disconnect from pigpoid
    pi.stop()

