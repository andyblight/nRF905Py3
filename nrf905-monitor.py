#!/usr/bin/env python3
""" Example program that uses the Nrf905 class to implement a simple text chat
system between two devices. """

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
    transceiver.set_frequency(434.25)
    transceiver.set_rx_address(0x43454749)
    # Optional to set before open is called.
    transceiver.set_tx_address(0x4345474a)
    transceiver.open(callback)
    quit = False
    while not quit:
        data = input("Enter data ('q' to quit) >")
        if data == "q" or data == "Q":
            quit = True
        else:
            transceiver.send(data)
    receiver.close()

if __name__ == "__main__":
    main()
