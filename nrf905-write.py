#!/usr/bin/env python3
""" Example program that uses the Nrf905 class to print out whatever is being received by the nRF905 device. """

from nrf905.nrf905 import Nrf905


def main():
    """ Create a transmitter instance. 
        Send a packet of up to 32 bytes.
    """

    receiver = Nrf905()
    receiver.open(434)
    # Bodge: should come from the command line arg.
    data_bytes = [20] * 32
    receiver.write(data_bytes)
    receiver.close()


if __name__ == "__main__":

    main()
