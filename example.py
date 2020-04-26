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
    packet_number = int(payload[0])
    packet_length = int(payload[1])
    packet_string = str(payload[2:])
    print("Received: {}, {}, '{}'".format(
        packet_number, packet_length, packet_string)


def main():
    """ Create a transceiver instance and set it up to print any data received.
    Give the user a prompt and send any data they enter.
    """
    test_mode = False
    transceiver = Nrf905()
    # Must be set before open is called.
    transceiver.frequency_mhz = 434.2
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
                data_packets_sent = 0
                while data:
                    # Send first 30 bytes as the payload.
                    packet = data[0:30]
                    payload = bytearray()
                    payload.extend(data_packets_sent)
                    payload.extend(len(packet))
                    payload.extend(packet.encode())
                    print("Sending packet", payload)
                    transceiver.send(payload)
                    # Take the first 30 bytes off the data.
                    data = data[30:]
                    data_packets_sent += 1
    # Close.
    transceiver.close()


if __name__ == "__main__":
    main()
