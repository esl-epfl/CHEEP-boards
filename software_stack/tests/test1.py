import sys
sys.path.append('../python/')

from cheep import *
from pyftdi.ftdi import Ftdi
from pyftdi.i2c import I2cController, I2cNackError

i2c = I2cController()


import subprocess
import re

# run the script and capture output
out = subprocess.check_output(
    ["python3", "/home/juan/.local/bin/ftdi_urls.py"],
    text=True
)

# ftdi://[vendor][:[product][:serial|:bus:address|:index]]/interface
# e.g. ftdi://ftdi:4232:3:67/2  (Quad RS232-HS)

# from iceprog
# -d <device string>    use the specified USB device [default: i:0x0403:0x6010 or i:0x0403:0x6014]
#                           d:<devicenode>               (e.g. d:002/005)
#                           i:<vendor>:<product>         (e.g. i:0x0403:0x6010)
#                           i:<vendor>:<product>:<index> (e.g. i:0x0403:0x6010:0)
#                           s:<vendor>:<product>:<serial-string>


# find the line that matches ftdi://.../2
m = re.search(r"(ftdi://ftdi:[0-9a-fA-F:]+/2)", out)
url = m.group(1) if m else None

print(url)

# then use it
i2c.configure(url)
cb = CheepBoard(i2c)
cb.pll.set_frequency(1_000_000)

# # Ensure the correct chewing gums are installed
# expected_configuration = {
#     1: {"type": "CurrentMeasurementSupply"},
#     2: {"type": "CurrentMeasurementSupply"},
#     3: {"type": "PosNegSupply"},
#     4: {"type": "CurrentMeasurementSupply"},
#     5: {"type": "CurrentMeasurementSupply"},
#     6: {"type": "PosNegSupply"},
#     7: {"type": "PosNegSupply"},
#     8: {"type": "CurrentMeasurementSupply"},
#     9: {"type": "PosNegSupply"},
#     10: {"type": "CurrentMeasurementSupply"},
#     11: {"type": "CurrentMeasurementSupply"},
#     12: {"type": "CurrentMeasurementSupply"}
# }
# cb.check_chewing_gums(expected_configuration)

# cb.enable_chewing_gums()
# cg1=cb.get_chewing_gum(1)