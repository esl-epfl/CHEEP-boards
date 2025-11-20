# cheep_deploy tool
cheep_deploy.py is used to program the EEPROM of the ChewingGum Boards

usage: cheep_deploy.py [-h] [-C CHEWING_GUM] [-w0 W0] [-w1 W1] ... [-w31 W31] [-P VIDPID] [-v] [-d] [device]

positional arguments:
  device                serial port device name

optional arguments:
  -h, --help            show this help message and exit
  -C CHEWING_GUM, --chewing_gum CHEWING_GUM
                        Chewing gum to program. Default = 1
  -w0 W0                Value of 32 bit word 0 at address 0x00
  -w1 W1                Value of 32 bit word 1 at address 0x04
  -w2 W2                Value of 32 bit word 2 at address 0x08
  -w3 W3                Value of 32 bit word 3 at address 0x0c
  -w4 W4                Value of 32 bit word 4 at address 0x10
  -w5 W5                Value of 32 bit word 5 at address 0x14
  -w6 W6                Value of 32 bit word 6 at address 0x18
  -w7 W7                Value of 32 bit word 7 at address 0x1c
  -w8 W8                Value of 32 bit word 8 at address 0x20
  -w9 W9                Value of 32 bit word 9 at address 0x24
  -w10 W10              Value of 32 bit word 10 at address 0x28
  -w11 W11              Value of 32 bit word 11 at address 0x2c
  -w12 W12              Value of 32 bit word 12 at address 0x30
  -w13 W13              Value of 32 bit word 13 at address 0x34
  -w14 W14              Value of 32 bit word 14 at address 0x38
  -w15 W15              Value of 32 bit word 15 at address 0x3c
  -w16 W16              Value of 32 bit word 16 at address 0x40
  -w17 W17              Value of 32 bit word 17 at address 0x44
  -w18 W18              Value of 32 bit word 18 at address 0x48
  -w19 W19              Value of 32 bit word 19 at address 0x4c
  -w20 W20              Value of 32 bit word 20 at address 0x50
  -w21 W21              Value of 32 bit word 21 at address 0x54
  -w22 W22              Value of 32 bit word 22 at address 0x58
  -w23 W23              Value of 32 bit word 23 at address 0x5c
  -w24 W24              Value of 32 bit word 24 at address 0x60
  -w25 W25              Value of 32 bit word 25 at address 0x64
  -w26 W26              Value of 32 bit word 26 at address 0x68
  -w27 W27              Value of 32 bit word 27 at address 0x6c
  -w28 W28              Value of 32 bit word 28 at address 0x70
  -w29 W29              Value of 32 bit word 29 at address 0x74
  -w30 W30              Value of 32 bit word 30 at address 0x78
  -w31 W31              Value of 32 bit word 31 at address 0x7c
  -P VIDPID, --vidpid VIDPID
                        specify a custom VID:PID device ID, may be repeated
  -v, --verbose         increase verbosity
  -d, --debug           enable debug mode

# Deploying a CurrentMeasurementSupply
- Chewing gum 1 (-C 1)
- ID 0x45534C01 (-w0 0x45534C01)
- 150mOhm Shunt resistor (-w1 150)
- INA212, i.e. gain 1000 -w2 1000
./cheep_deploy.py -C 1 -w0 0x45534C01 -w1 150 -w2 1000 ftdi://ftdi:4232:1:1/2

# Deploying a PosNegSupply
- Chewing gum 1 (-C 1)
- ID 0x45534C02 (-w0 0x45534C02)
./cheep_deploy.py -C 1 -w0 0x45534C02 ftdi://ftdi:4232:1:1/2