#!/bin/bash
# Runs all nRF905 not connected tests.

#DEBUG = -v

python3 -m unittest ${DEBUG} test_nrf905gpio test_nrf905spinc
