# nRF905 Python 3 module

This project is based around the nrf905 class that interfaces with the pigpoid.

The pigpoid does all the tricky interfacing with the GPIO pins and the SPI bus
and the nrf905 class handles all the nRF905 specific things like waggling the
GPIO pins at the right time.

In addition, there are two demo programs that use the nrf05 class.  One is a
monitor program that prints out whatever is received by the nRF905 device.  The
other transmits 32 bits (8 hex chars).

Finally, there is a test harness that tests the nrf905 class.  Execute it by
running:

```bash
./run-tests.py
```

## Wiring

### The nRF905 board

Looking at the top (the side with the antenna sticking up) the nRF905 module
pin out is:

```Z
 __________________________________________________
| VCC         TxEN                                 |
| CE          PWR                                  |
| CLK         CD                                   |
| AM          DR            CHIP          ANTENNA  |
| MISO        MOSI                                 |
| SCK         CSN                                  |
| GND         GND                                  |
|__________________________________________________|
```

### RPi to nRF905

The RPi is connected to SPI0 and some GPIO pins as follows:

```Z
RPi                         nRF905
Pin No.     Name            Board   Datasheet   Notes
11          GPIO17          PWR     PWR_UP      0 = standby, 1 = working
12          GPIO18          DR      DR          1 = Data ready (resistor)
15          GPIO22          TxEN    TX_EN       0 = receive, 1 = transmit
16          GPIO23          CD      CD          1 = Carrier detetcted (resistor)
17          3V3             VCC
18          GPIO24          AM      AM          1 = Address matched (resistor)
19          GPIO10          MOSI
21          GPIO9           MISO
22          GPIO25          CE      TRX_CE      0 = disable, 1 = enable
23          GPIO11          SCK
24          GPIO8           CSN
25          GND             GND
```

Where it says (resistor), use a 1k resistor.
The AM and CD pins are optional.  Adding these pins improves control of the
devices.  The CD pin improves transmission by only transmitting when the carrier
is not detected.  The AM pin can be used to determine if the data packet is
valid or not.

## References

This blog post has a lot of useful info in it.
<http://blog.zakkemble.net/nrf905-avrarduino-librarydriver/>
