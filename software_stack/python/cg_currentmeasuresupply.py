import cheep

class CG_CurrentMeasureSupply(cheep.ChewingGum):
    def __init__(self,cb,id):
        super().__init__(cb,id)
        self.shunt_mOhms = self[1]
        self.gain = self[2]
        self.type="CurrentMeasurementSupply"
    def __str__(self):
        return "CurrentMeasurementSupply with ID 0x{:8x} / {} / {}mOhms / gain {}".format(self.get_id(), self.get_eui64(), self.shunt_mOhms, self.gain)
    def set_voltage(self,value):
        pass
    def get_voltage(self,value):
        pass
    def get_current(self,value):
        pass