#!/usr/bin/env python3
""" Example program that uses the nRF905 class to print out whatever is being received by the nRF905 device. """

from nRF905.nRF905 import nRF905


def main():
    """ Create a receiver instance and set it up to receive. 
        When data is received, print it out.
        Loop until a key is pressed.
    """

    receiver = nRF905()
    receiver.open()
    key_pressed = False
    while not key_pressed:
        # Check for key press
        key_pressed = True
    receiver.close()


if __name__ == "__main__":

    main()
