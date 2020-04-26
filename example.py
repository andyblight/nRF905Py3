#!/usr/bin/env python3
""" Example program that uses the Nrf905 class to implement a simple text chat
system between two devices.
"""

import time

from nrf905.nrf905 import Nrf905



def callback(payload):
    """ Print out the contents of the payload.
    The payload is a bytearray so convert to a string for printing.
    """
    string = str(payload)
    print("Received:", string)


def main():
    """ Create a transceiver instance and set it up to print any data received.
    Give the user a prompt and send any data they enter.
    """
    test_mode = False
    transceiver = Nrf905()
    # Must be set before open is called.
    transceiver.frequency_mhz = 434.5
    # Setup to listen for any replies.
    # Callback will be fired if anything is received.
    # transceiver.receive_address = 0x43454749
    transceiver.receive_address = 0x4345474A
    transceiver.enable_receive(callback)
    # Can also be called after open is called.
    # transceiver.transmit_address = 0x4345474A
    transceiver.transmit_address = 0x43454749
    # Open the transceiver.  Transmit only is default.
    transceiver.open()
    time.sleep(0.02)
    # Send whatever data the user enters until quit.
    if test_mode:
        payload = bytearray()
        payload.extend("Test data 12345".encode())
        print("Sending packet", payload)
        transceiver.send(payload)
        time.sleep(1)
    else:
        quit = False
        while not quit:
            data = input("Enter data ('q' to quit) >")
            if data == "q" or data == "Q":
                quit = True
            else:
                while data:
                    # Send first 32 bytes as the payload.
                    packet = data[0:32]
                    payload = bytearray()
                    payload.extend(packet.encode())
                    print("Sending packet", payload)
                    transceiver.send(payload)
                    # Take the first 32 bytes off the data.
                    data = data[32:]
    # Close.
    transceiver.close()


if __name__ == "__main__":
    main()
