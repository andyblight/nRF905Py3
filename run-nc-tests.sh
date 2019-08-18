#!/bin/bash
# Runs all nRF905 not connected tests.

python3 -m unittest -v test_nrf905gpio test_nrf905spinc
