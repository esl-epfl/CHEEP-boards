import cheep

class CG_CurrentMeasureSupply(cheep.ChewingGum):
    def __init__(self,cb,id):
        super().__init__(cb,id)
        self.shunt_mOhms = self[1]
        self.gain = self[2]
        self.type="CurrentMeasurementSupply"
    def __str__(self):
        return "CurrentMeasurementSupply with ID 0x{:8x} ({}) / {} / {}mOhms / gain {}".format(self.get_id(),bytes.fromhex(self.get_id()[2:]).decode(), self.get_eui64(), self.shunt_mOhms, self.gain)
    def check(self, configuration):
        if "type" in configuration:
            expected = configuration["type"]
            assert self.type == expected, f"CG missmatch on {self.id}: expected {expected}, found {self.type}"
        if "shunt" in configuration:
            pass
    def set_voltage(self,value):
        pass
    def get_voltage(self,value):
        pass
    def get_current(self,value):
        pass