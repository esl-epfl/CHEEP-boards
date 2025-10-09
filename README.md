# This repository contains the CHEEP testing boad as well as the chewing gum programmable supply boards 

The CHEEP board uses I2C as the measurement and control interface for  
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
