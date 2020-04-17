#!/usr/bin/env python3
""" Example program that uses the Nrf905 class to implement a simple text chat
system between two devices. 32 chars max per line!
"""

from nrf905.nrf905 import Nrf905


def callback(data):
    """ Print out the contents of the data received. """
    print("Received:", data)


def main():
    """ Create a transceiver instance and set it up to print any data received.
    Give the user a prompt and send any data they enter.
    """
    transceiver = Nrf905()
    # Must be set before open is called.
    transceiver.frequency = 434.5
    transceiver.receive_address = 0x43454749
    # Can also be called after open is called.
    transceiver.transmit_address = 0x4345474A
    # Open the transceiver.
    transceiver.open(callback)
    # Send whatever data the user enters until quit.
    quit = False
    while not quit:
        data = input("Enter data ('q' to quit) >")
        if data == "q" or data == "Q":
            quit = True
        else:
            while data:
                # Send first 32 bytes as the payload.
                payload = data[0:32]
                transceiver.send(payload)
                # Take the first 32 bytes off the data.
                data = data[32:]
    # Close.
    transceiver.close()


if __name__ == "__main__":
    main()