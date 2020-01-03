#!/bin/bash
# Runs all nRF905 Raspberry Pi tests with the nRF905 module not connected.

#DEBUG = -v

python3 -m unittest ${DEBUG} nrf905.test_nrf905_config nrf905.test_nrf905_gpio
