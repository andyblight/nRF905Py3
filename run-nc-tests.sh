#!/bin/bash
# Runs all nRF905 not connected tests.

#DEBUG = -v

python3 -m unittest ${DEBUG} nrf095.test_nrf905_gpio nrf905.test_nrf905_spi_nc
