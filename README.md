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

## Preparing the RPi

Firstly (and probably most importantly) is to enable the SPI interface.  This actually loads a kernel module that communicates with the SPI bus and without this module, nothing works!
Secondly, you need to start the pigpio daemon using

```bash
sudo pigpiod
```

## Wiring

### The nRF905 board

Looking at the top (the side with the antenna sticking up) the nRF905 pin out is:

```Z
 __________________________________________________
| VCC         TxEN                                 |
| CE          PWR                                  |
| UCK         CD                                   |
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
The AM and CD pins are optional.  Adding these pins improves control of the devices.
The CD pin improves transmission by only transmitting when the carrier is not detected.
The AM pin can be used to determine if the data packet is valid or not.

NOTE: The file 'wiring.txt' shows the colours of the wires I used during development.

## Tests

The tests have been written with the aim of getting the code working with the
nRF905.  There are three sets of tests, each invoked by a different shell script.

### run-pc-tests.sh

Runs tests that can be run on the host PC (does not use pigpio or the nRF905).

### run-nc-tests.sh

Runs tests that must be run on the Raspberry Pi (calls pigpio) but does not try to use the nRF905 module.

### run-c-tests.sh

Runs tests that must be run on the Raspberry Pi (calls pigpio) and has the nRF905 module connected (tries to use registers on the device).

## Design

The code is arranged in a number of modules.

```Z
     ____________________________________
    |             nrf905.py              |
    |____________________________________|
     ________________    ________________    __________________
    | nrf905_gpio.py |  | nrf095_spi.py  |  | nrf905_config.py |
    |________________|  |________________|  |__________________|
     ____________________________________
    |              pigpio                |
    |____________________________________|

```

TODO EXPLAIN HOW nfrf905.py IS DESIGNED.

### nrf905.py

Implements the class Nrf905.

This class forms the interface that most coders will use.  An instance of this class will use one Nrf905Gpio object and one Nrf905Spi object.  These objects are used together to control the nRF905 module.

Depends on Nrf905GPio and Nrf905Spi.

### nrf905_gpio.py

Implements the class Nrf905Gpio.

Responsible for controlling and responding to the GPIO pins used by the nRF905 module.

Depends on pigpio.

### nrf905_spi.py

Implements the class Nrf905Spi.

Responsible for reading and writing messages using the SPI bus via the pigpio commands.  Also uses Nrf905ConfigRegister to read and write to the nRF905 config register.

Depends on Nrf905ConfigRegister and pigpio.

### nrf905_config.py

Implements the class Nrf905ConfigRegister.  During development, this was split out from the Nrf905Spi class as it became so big.  Splitting it out also made unit testing of this whole class much easier.

No dependencies.

## TO DO List

1. Make nrf905-monitor work.
    1. Nrf905 is part way through a re-write as handling states was getting difficult.
        1. Use setters and getters for exposed properties. DONE.
        1. threads.py can be used as an example of how to use threads, queues and semaphores to do what I need.  Merge in changes.
        1. Use state machine in prototypes dir instead of variables.
1. Add SPI bus 1 functionality.  The Nrf905Spi.\_\_init\_\_() function takes the spi_bus parameter but there is no implemented functionality.  Affects Nrf905SPI and Nrf905Gpio classes.  Needs RPi 2 or later to test.
1. Deal with multiple users and one device problem.  Only allow single users?  Allow multiple users using queues and callbacks?  Multiple users means using queues, each user need unique handle (in the Nrf905 class).  Need to work out user privileges for each function.

## References

This blog post has a lot of useful info in it.
<http://blog.zakkemble.net/nrf905-avrarduino-librarydriver/>
