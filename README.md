# nRF905 Python 3 module

This project is based around the Nrf905 class that interfaces with the pigpoid.

The pigpoid does all the tricky interfacing with the GPIO pins and the SPI bus
and the Nrf905 class handles all the nRF905 specific things like waggling the
GPIO pins at the right time.

In addition, there are two demo programs that use the nrf05 class.  One is a
monitor program that prints out whatever is received by the nRF905 device.  The
other transmits 32 bits (8 hex chars).

Finally, there is a test harness that tests the Nrf905 class.  Execute it by
running:

```bash
./run-tests.py
```

## Wiring

### The nRF905 board

Looking at the top (the side with the antenna sticking up) the nRF905 pin out is:

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

The RPi can support two nRF905 devices.  The following table shows how to wire
up each module.

```Z
RPi           pigpio      nRF905
Pin  Name     SPI pins    No. Board   Datasheet   Notes
01   3V3                  1   VCC
02   5V0
03   GPIO2
04   5V0
05   GPIO3
06   GND
07   GPIO4
08   GPIO14               1   TxEN    TX_EN       0 = receive, 1 = transmit
09   GND
10   GPIO15               0   TxEN    TX_EN       0 = receive, 1 = transmit
11   GPIO17   Aux CE1     1
12   GPIO18   Aux CE0     1   CSN
13   GPIO27               0   CE      TRX_CE      0 = disable, 1 = enable
14   GND
15   GPIO22               0   PWR     PWR_UP      0 = standby, 1 = working
16   GPIO23               0   CD      CD          1 = Carrier detetcted (resistor)
17   3V3                  0   VCC
18   GPIO24               0   AM      AM          1 = Address matched (resistor)
19   GPIO10   Main MOSI   0   MOSI
20   GND
21   GPIO9    Main MISO   0   MISO
22   GPIO25               0   DR      DR          1 = Data ready (resistor)
23   GPIO11   Main SCLK   0   SCK
24   GPIO8    Main CE0    0   CSN
25   GND                  0   GND
26   GPIO7    Main CE1
27   ID_SD
28   ID_SC
29   GPIO5                1   CE      TRX_CE      0 = disable, 1 = enable
30   GND
31   GPIO6                1   PWR     PWR_UP      0 = standby, 1 = working
32   GPIO12               1   CD      CD          1 = Carrier detetcted (resistor)
33   GPIO13               1   AM      AM          1 = Address matched (resistor)
34   GND
35   GPIO19   Aux MISO    1   MISO
36   GPIO16   Aux CE2
37   GPIO26               1   DR      DR          1 = Data ready (resistor)
38   GPIO20   Aux MOSI    1   MOSI
39   GND                  1   GND
40   GPIO21   Aux SCLK    1   SCK
```

Where it says (resistor), use a 1k resistor.
The AM and CD pins are optional.  Adding these pins improves control of the
devices.  The CD pin improves transmission by only transmitting when the carrier
is not detected.  The AM pin can be used to determine if the data packet is
valid or not.

## References

This blog post has a lot of useful info in it.
<http://blog.zakkemble.net/nrf905-avrarduino-librarydriver/>
