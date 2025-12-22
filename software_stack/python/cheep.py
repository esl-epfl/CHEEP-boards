from pyftdi.i2c import I2cController, I2cNackError
from pll_i2c_wrapper import I2CWrapper as pllI2CWrapper
from pll_controller import PLLController
from pll_registers import PLLReg

I2C_TREE = {
    "MBID" : {"SW":{0x70:0, 0x71:1<<7}, "label": "Mainboard EEPROM"},
    "MBIF" : {"SW":{0x70:1<<7, 0x71:0}, "label": "Mainboard Infrastructure"},
    "CHEEP": {"SW":{0x70:1<<6, 0x71:0}, "label": "Cheep Chip Testing PCB"},
    "EXT"  : {"SW":{0x70:0, 0x71:1<<6}, "label": "External I2C Interface"},
    "CG1"  : {"SW":{0x70:1<<2, 0x71:0}, "label": "Chewing Gum Board 1"},
    "CG2"  : {"SW":{0x70:1<<1, 0x71:0}, "label": "Chewing Gum Board 2"},
    "CG3"  : {"SW":{0x70:1<<0, 0x71:0}, "label": "Chewing Gum Board 3"},
    "CG4"  : {"SW":{0x70:1<<3, 0x71:0}, "label": "Chewing Gum Board 4"},
    "CG5"  : {"SW":{0x70:1<<4, 0x71:0}, "label": "Chewing Gum Board 5"},
    "CG6"  : {"SW":{0x70:1<<5, 0x71:0}, "label": "Chewing Gum Board 6"},
    "CG7"  : {"SW":{0x70:0, 0x71:1<<0}, "label": "Chewing Gum Board 7"},
    "CG8"  : {"SW":{0x70:0, 0x71:1<<1}, "label": "Chewing Gum Board 8"},
    "CG9"  : {"SW":{0x70:0, 0x71:1<<2}, "label": "Chewing Gum Board 9"},
    "CG10" : {"SW":{0x70:0, 0x71:1<<5}, "label": "Chewing Gum Board 10"},
    "CG11" : {"SW":{0x70:0, 0x71:1<<4}, "label": "Chewing Gum Board 11"},
    "CG12" : {"SW":{0x70:0, 0x71:1<<3}, "label": "Chewing Gum Board 12"}
}

class CheepBoard:
    def __init__(self, i2c):
        self.i2c = i2c
        self.cg_en_io_exp_addr = 0x21
        self.set_i2c_mode()
        self.current_i2c_mux = None
        self.pll = PLLController(CheepPllI2CWrapper(self))

    def set_i2c_mode(self):
        gpio = self.i2c.get_gpio()
        gpio.set_direction(0x20, 0x20)
        gpio.write(0x20)

    def set_i2c_mux(self, ID):
        if ID in I2C_TREE and self.current_i2c_mux != ID:
            for i2c_addr,i2c_data in I2C_TREE[ID]["SW"].items():
                port = self.i2c.get_port(i2c_addr)
                port.write([i2c_data])
            self.current_i2c_mux = ID

    def scan_cheep_tree(self):
        pass

    def print_cheep_tree(self):
        pass
    def get_chewing_gum(self,idx):
        if idx==0:
            ID="MBID"
        elif idx<=12:
            ID="CG{}".format(idx)
        else:
            return None
        return self.get_chewing_gum_by_name(ID)
    def get_chewing_gum_by_name(self, ID):
        eeprom = ChEEPROM(self, ID)
        if eeprom.get_eui64() != None:
            id = eeprom.get_id()
            if id in CG_BOARD_MAP:
                return CG_BOARD_MAP[id](self, eeprom.id)
            else:
                return ChewingGum(self, eeprom.id)
        return None

    def enable_chewing_gums(self, masks=(0xff,0x0f)):
        self.set_i2c_mux("MBIF")
        port = self.i2c.get_port(self.cg_en_io_exp_addr)
        # set the chewing gum enable pins at outputs
        port.write_to(0x6,[0x00])
        port.write_to(0x7,[0xf0])
        port.write_to(0x2, [masks[0]])
        port.write_to(0x3, [masks[1]])

    def disable_chewing_gums(self, masks=(0x00,0x00)):
        self.set_i2c_mux("MBIF")
        port = self.i2c.get_port(self.cg_en_io_exp_addr)
        port.write_to(0x6,[0x00])
        port.write_to(0x7,[0xf0])
        port.write_to(0x2, [masks[0]])
        port.write_to(0x3, [masks[1]])

    def check_chewing_gums(self,configuration):
        for (idx,conf) in configuration.items():
            cg = self.get_chewing_gum(idx)
            assert cg != None, f"CG{idx} is missing."
            cg.check(conf)

class CheepPllI2CWrapper(pllI2CWrapper):
    def __init__(self,cb,device_address=0x60):
        cb.set_i2c_mux("MBIF")
        super().__init__(device_address)
        self.cb=cb

    def write_data(self, reg: int, data: int) -> None:
        """
        Write data to the specified register_address on the I2C device.

        Parameters:
            reg (int): Address of the register to write data to.
            data (int): Data to be written to the register.
        """
        self.cb.set_i2c_mux("MBIF")
        msg = bytearray()
        msg.append(data)
        self.cb.i2c.get_port(self.addr).write_to(reg, msg)

    def read_data(self, reg: int, num_bytes: int = 1) -> int:
        """
        Read data from the specified register_address on the I2C device.

        Parameters:
            reg (int): Address of the register to read data from.
            num_bytes (int, optional): Number of bytes to read. Default to 1.

        Returns:
            int: Data read from the register.
        """
        self.cb.set_i2c_mux("MBIF")
        data = self.cb.i2c.get_port(self.addr).read_from(reg,num_bytes)
        data = int.from_bytes(data, byteorder ="big") #read value from PyFtdi gives back bytearray but pll_register needs integer
        return data


class ChEEPROM:
    def __init__(self,cb,id):
        self.cb = cb
        self.id = id
        self.eeprom_addr=0x50
        self.wordsize=4
        self.base_address=0x0

    def __str__(self):
        return("ChEEPROM 0x{:4x} / {}".format(self.get_id(), self.get_eui64()))

    def __getitem__(self,idx):
        self.select_i2c()
        port = self.cb.i2c.get_port(self.eeprom_addr)
        return int.from_bytes(port.read_from(self.base_address+self.wordsize*idx,self.wordsize),byteorder="big",signed=False)
    def __setitem__(self,idx,val):
        self.select_i2c()
        port = self.cb.i2c.get_port(self.eeprom_addr)
        try:
            b = val.to_bytes(4,byteorder="big",signed=False)
            port.write_to(self.base_address+idx*self.wordsize,b)
        except I2cNackError:
            return None

    def select_i2c(self):
        self.cb.set_i2c_mux(self.id)
        # for i2c_addr,i2c_data in self.id.items():
        #     port = self.cb.i2c.get_port(i2c_addr)
        #     port.write([i2c_data])
    def get_eui48(self):
        self.select_i2c()
        port = self.cb.i2c.get_port(self.eeprom_addr)
        try:
            b = port.read_from(0xfA,6)
            return  ":".join(["{:02X}".format(c) for c in b])
        except I2cNackError:
            return None
    def get_eui64(self):
        self.select_i2c()
        port = self.cb.i2c.get_port(self.eeprom_addr)
        try:
            b = port.read_from(0xfA,6)
            d = b[:3] + b'\xff\xfe' + b[3:]
            return  ":".join(["{:02X}".format(c) for c in d])
        except I2cNackError:
            return None
    def get_id(self):
        self.select_i2c()
        port = self.cb.i2c.get_port(self.eeprom_addr)
        try:
            b = port.read_from(0x0,4)
            return int.from_bytes(b,byteorder="big",signed=False)
        except I2cNackError:
            return None

class ChewingGum(ChEEPROM):
    def __init__(self,cb,id):
        super().__init__(cb,id)
        self.type="UnknownChewingGum"
    def __str__(self):
        return "Unknown ChewingGum with ID 0x{:8x} ({}) / {}".format(self.get_id(), bytes.fromhex(f"{self.get_id():08x}").decode(),self.get_eui64())
    def check(self, configuration):
        if "type" in configuration:
            expected = configuration["type"]
            assert self.type == expected, f"CG missmatch on {self.id}: expected {expected}, found {self.type}"

class CG_Uninitialised(ChewingGum):
    def __str__(self):
        self.type="UninitialisedChewingGum"
        return "Uninitialised ChewingGum {}".format(self.get_eui64())

from cg_currentmeasuresupply import CG_CurrentMeasureSupply
from cg_posnegsupply import CG_PosNegSupply

# This maps the chewing gum IDs to their classes
CG_BOARD_MAP = {
    0x45534C01: CG_CurrentMeasureSupply,
    0x45534C02: CG_PosNegSupply,
    0xffffffff: CG_Uninitialised
}
