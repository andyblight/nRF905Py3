# nRF905 Python 3 module

This project is based around the nRF905 class that interfaces with the pigpoid.

The pigpoid does all the tricky interfacing with the GPIO pins and the SPI bus
and the nRF905 class handles all the nRF905 specific things like waggling the
GPIO pins at the right time.

In addition, there are two demo programs that use the nRF905 class.  One is a
monitor program that prints out whatever is received by the nRF905 module.  The
other transmits 32 bits (8 hex chars).

Finally, there is a test harness that tests the nRF905 class.
