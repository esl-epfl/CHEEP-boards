import cheep

class CG_PosNegSupply(cheep.ChewingGum):
    def __init__(self,cb,id):
        super().__init__(cb,id)
        self.type="PosNegSupply"
    def __str__(self):
        return "PosNegSupply with ID 0x{:8x} / {}".format(self.get_id(), self.get_eui64())
    def set_voltage(self,value):
        pass