#!/usr/bin/env python3
""" Example program that uses the nRF905 class to print out whatever is being received by the nRF905 device. """

from nRF905.nRF905 import nRF905


def main():
    """ Create a transmitter instance. 
        Send a packet of up to 32 bytes.
    """

    receiver = nRF905()
    receiver.open(434)
    # Bodge: should come from the command line arg.
    data_bytes = [20] * 32
    receiver.write(data_bytes)
    receiver.close()


if __name__ == "__main__":

    main()
