#!/bin/bash
# Runs all nRF905 not connected tests.

#DEBUG = -v

python3 -m unittest ${DEBUG} nrf905.test_nrf905_config nrf905.test_nrf905_state_machine
