#!/bin/bash
# Format and check all Python files.
set -e

black -l 79 nrf905 *.py
flake8 nrf905 *.py

echo "Please ignore this E203 error:"
echo "nrf905/nrf905_spi.py:107:22: E203 whitespace before ':'"
echo "flake8 has a bug and is waiting for a fix."
echo

