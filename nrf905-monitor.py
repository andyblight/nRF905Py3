#!/usr/bin/env python3
""" Example program that uses the nRF905 class to print out whatever is being received by the nRF905 device. """

from nrf905.nrf905 import nrf905

def callback(data):
    """ Prints out the contents of the data received. """
    print("callback", data)

def main():
    """ Create a receiver instance and set it up to receive. 
        When data is received, print it out.
        Loop until a key is pressed.
    """
    receiver = nrf905()
    receiver.open(434, callback)
    input("Press enter to quit...")
    receiver.close()


if __name__ == "__main__":

    main()
