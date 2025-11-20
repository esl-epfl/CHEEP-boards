import sys
sys.path.append('../python/')

from cheep import *
from pyftdi.ftdi import Ftdi
from pyftdi.i2c import I2cController, I2cNackError

i2c = I2cController()
i2c.configure("ftdi://ftdi:4232:1:1/2")
cb = CheepBoard(i2c)
cb.pll.set_frequency(100_000_000)

# Ensure the correct chewing gums are installed
expected_configuration = {
    1: {"type": "CurrentMeasurementSupply"},
    2: {"type": "CurrentMeasurementSupply"},
    3: {"type": "PosNegSupply"},
    4: {"type": "CurrentMeasurementSupply"},
    5: {"type": "CurrentMeasurementSupply"},
    6: {"type": "PosNegSupply"},
    7: {"type": "PosNegSupply"},
    8: {"type": "CurrentMeasurementSupply"},
    9: {"type": "PosNegSupply"},
    10: {"type": "CurrentMeasurementSupply"},
    11: {"type": "CurrentMeasurementSupply"},
    12: {"type": "CurrentMeasurementSupply"}
}
cb.check_chewing_gums(expected_configuration)

cb.enable_chewing_gums()
cg1=cb.get_chewing_gum(1)