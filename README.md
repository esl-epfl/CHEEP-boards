# Welcome to the CHEEEP boards!

This is a set of PCBs to test, in principle, [X-HEEP](github.com/esl-epfl/x-heep) chips (CHEEPs)... but, you can use it to test any chip you want, for what it matters.

The general idea is to recycle efforts, so all the things that are common to any CHEEP were moved into a **main board**. This one includes an FTDI through which you can program or communicate with your cheep, as well as some peripherals like flash, buttons, LEDs, etc. The main board also generates all the voltages needed by these blocks.

On the sides of the main board you will find slots for **chewing gums**, these are chewing-gum-shaped custom-boards that can do pretty much whatever you want them to. We have designed some that provide a configurable voltage and the extras needed to measure current being drained.

Almost everything that is on the main board, including the outputs of the chewing gums, go to a large 150-positions connector at the bottom of the PCB. You can then design for each cheep a custom **breakout board** that takes the signals that you need from that connector.

Bellow you can find some extra information on each of these parts.

## Main board

The objective of the mainboard is to include everything your cheep needs so that your breakout board can be as simple as a footprint for your cheep/socket wired to the connector.

It is controlled through a USB-C connector directly from your PC. From that USB you can power up the whole board and control the FTDI.

You can alternativelly power up the board with an external DC power supply through the jack of banana connector.

The FTDI is the same used on the [EPFL programmer](github.com/esl-epfl/x-heep-programmer-pmod), so you can directly command it through the `make` commands on X-HEEP.

The UART of the FTDI is also made available in the same way that it was on X-HEEP, so you just open picocom or any serial viewer to read the UART output of your CHEEP from your PC.

We use level shifters all around so that your chip can operate at any IO voltage you want. You can select the IO voltage on the main board through some jumpers with pre-defined values, or with a trimmer.

Additionally, through the FTDI you can control any of the I2C devices on the board, on the chewing gums, or on the breakout board. Check the [Software stack](./software_stack/) for the python tools for this. Components that are mapped include:
* **GPIO expanders** - so you can control (read/write) GPIOs and interface with your cheep through them (software stack pending)
* **PLL** - You can supply your cheep with different clocks, from 4 kHz to 200 MHz. Just check the [PLL software stack](./software_stack/python/pll_controller.py).
* **Chewing gums** - You can configure things on the chewing gums (e.g. read from on-board ADCs or set DAC values).

### 🪲 Bugs and needed improvements
* We need contributions on the software stack to control the chewing gums and on-board GPIOs.
* Setting different on-board IO voltages introduces weird behaviors on the LEDs, some of which are floating to be controlled by the breakout board. We should handle this better.

## 150 positions connector

You cancheck the [standard](./docs/150%20pin%20cheep%20board%20connector%20standard.pdf):

<img src="./docs/150 pin cheep board connector standard.png" width="100%" style="display:inline-block;">
</p>

There is also a symbol and footprint you can use in your PCB to make sure you are using the right assignment.

## Chewing gums

So far we have designed 2 chewing gums that can be found on [the chewing gum folder](./chewing-gums/):

### PosNeg supply
As the name suggests, allows to produce a positive or negative supply (from the main-board-generated -5V reference).

### Current Measurement Supply

It's an voltage reference with a shunt to measure current. You can:
* Set the LDO reference through an on-board trimmer.
* Set the LDO reference through an on-board DAC (needs software stack to command it through I2C)
* Put different SMD resistor values (needs soldering :/)
* The shunt's voltage drop is amplified by an on-board amplifier (INA). Its output is made available on the SMA connector on the back. You can configure its gain through some pads on the bottom. You better measure against a known current before using these (e.g. I have measured the gain to be 1729 V/V with a 12 µV input referred offset with the default configurations). This will strongly affect your measurements!
* We left a 1 MΩ resistor to ground that you can use to make this calibration measurement.

## Creating your own

You can create your own chewing gum and contribute it to this project. You can use [the template](./chewing-gums/template/) to make sure you use the right footprint and pinout :)

### 🪲 Bugs and needed improvements
* We missed a 180 kΩ resistor in series between the DAC output and the LDO reference (in case you want to control them through DAC)
* It would be nice to have a TH connector for the shunt in case you want to use different ranges
* It would be nice to have a TH connector for the LDO resistive divider in case you want to use different ranges

## Your custom breakout board

You can make your own custom breakout board to take things from the main board and chewing gums. Whatever you are missing, you can always just add it to the breakout board, it ain't illegal...

You can take [the HEEPidermis breakout board](https://github.com/esl-epfl/HEEPidermis-breakout-board/tree/main) as an example.


## I2C Address Tree
The CHEEP mainboard uses TI TCA9548A (https://www.ti.com/lit/ds/symlink/tca9548a.pdf) I2C Multiplexers in order to allow to isolate the chewing gum boards from each other and to minimise the risk of I2C address conflicts.
### 0b1110000 / 0x70 - Left I2C Expander
#### PORT 0 - Chewing gum board 3
#### PORT 1 - Chewing gum board 2
#### PORT 2 - Chewing gum board 1
#### PORT 3 - Chewing gum board 4
#### PORT 4 - Chewing gum board 5
#### PORT 5 - Chewing Gum Board 6
#### PORT 6 - CHEEP CHIP PCB Connector
#### PORT 7 - CHEEP Board Infrastructure
#####
### 0b1110000 / 0x70 - Right I2C Expander
