from pll_controller import PLLController
from pll_registers import PLLReg
import sys

class I2CWrapper:
    """
    A base class for interfacing with I2C devices.

    This class provides common functionality for communicationg with I2C devices, 
    such as reading and writing data to registers.

    Attributes:
        addr (int): Address of the I2C device.
    """
    def __init__(self, device_address: int) -> None:
        """
        Initialize the I2CWrapper with the given device_address.
        
        Parameters:
            device_address (int): Address of the I2C device.
        """
        self.addr = device_address  

    def write_data(self, reg: int, data: int) -> None: 
        """
        Write data to the specified register_address on the I2C device.

        Parameters:
            reg (int): Address of the register to write data to.
            data (int): Data to be written to the register.
        """
        pass


    def read_data(self, reg: int, num_bytes: int = 1) -> int:
        """
        Read data from the specified register_address on the I2C device.

        Parameters:
            reg (int): Address of the register to read data from.
            num_bytes (int, optional): Number of bytes to read. Default to 1.

        Returns:
            int: Data read from the register.
        """
        return 0
        
        
    def pll_stuck(self) -> int:
        """
        Check Crystal Loff of Signal.

        Returns:
            int: 0 if valid crystal signal at the XA and XB Pins, i if loss of crystal signal detected.
        Reference:
            https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/application-notes/AN619.pdf#page=14
        """
        status = self.read_data(0)  & 0b00001000
        return status

class I2CPyFtdi(I2CWrapper):
    """
    A class for interfacing with I2C devices using PyFtdi libary.
    
    This class provides functionality to communicate with i2C devices
    using an FTDI USB-to-I2C adapter through the PyFtdi libary.

    Class Attributes:
        I2cController: The PyFtdi I2C controller class.
    Attributes:
        ftdi_address (str): The address of the FTDI USB-to-I2C adapter.
        i2c: The PyFtdi I2C controller instance.
        slave: The PyFtdi I2C slave port instance.
    
    """

    def __init__(self, ftdi_address: str, device_address: int = 0x60) -> None:
        """
        Initialize the I2CPyFtdi object.

        Parameters:
            ftdi_address (str): The address of the FTDI USB-to-I2C adapter.
            device_address (int, optional): The default I2C device address. Defaults to 0x60.

        Raises:
            EnviromentError: If the PyFtdi libarary is not available in the Python enviroment.
        """
        super().__init__(device_address)
        try:
            from pyftdi.i2c import I2cController 
            self.I2cController = I2cController
        except ImportError:
            raise OSError("This class requires Python enviroment")
        
        self.ftdi_address = ftdi_address
        self.ftdi_init()

    def ftdi_init(self) -> None:
        """
        Initialize the FTDI USB-to-I2C adapter.
        """
        self.i2c = self.I2cController()
        self.i2c.configure(self.ftdi_address)
        self.slave = self.i2c.get_port(self.addr)

    def write_data(self, reg: int, data: int) -> None: 
        """
        Write data to the specified register_address on the I2C device.

        Parameters:
            reg (int): Address of the register to write data to.
            data (int): Data to be written to the register.
        """
        msg = bytearray()
        msg.append(data)
        self.i2c.get_port(self.addr).write_to(reg, msg) 


    def read_data(self, reg: int, num_bytes: int = 1) -> int:
        """
        Read data from the specified register_address on the I2C device.

        Parameters:
            reg (int): Address of the register to read data from.
            num_bytes (int, optional): Number of bytes to read. Default to 1.

        Returns:
            int: Data read from the register.
        """
        data = self.i2c.get_port(self.addr).read_from(reg,num_bytes)
        data = int.from_bytes(data, byteorder ="big") #read value from PyFtdi gives back bytearray but pll_register needs integer
        return data



if __name__ == "__main__":
    # Example usage of the I2CWrapper and PLLController classes
    # Example usage of the I2CWrapper and PLLController classes
    roundit = False
    #i2c_object = I2CPyFtdi('ftdi://ftdi:4232:2:11/1', PLLReg.PLL_I2C_ADDRESS_PyFtdi)
    i2c_object = I2CPico(PLLReg.PLL_I2C_ADDRESS_PICO)

   #initalize PLL Controller and choose between PLL A or PLL B to configure each PLL
    pll_controller = PLLController(i2c_object)

    # Set the PLL frequency
    target_frequency = 80_000  # Example frequency in Hz
    pll_controller.set_frequency(target_frequency, 2, PLLReg.PLL_A)
    
    freq_array = [300_000_000, 4_000]

    start_freq = 100_000_000
    end_freq = 200_000_000
    step_size = 1_000_000
    period = 300
    output = 2
    pll = PLLReg.PLL_A
    amount = 100

    #pll_controller.hopping_freq(freq_array, amount, period, output, pll, roundit)

    #pll_controller.sweep_freq(start_freq, end_freq, step_size, period, output, pll, roundit)  