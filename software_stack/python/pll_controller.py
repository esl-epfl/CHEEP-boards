#from machine import Pin, I2C
from pll_i2c_wrapper import *
from pll_registers import PLLReg
#from utime import sleep_ms
from time import sleep



class PLLController:
    """
    Control PLL frequencies using an I2CWrapper.

    Attribuites:
        crystalFreq (int): Frequency of the srystal oscillator.

    Parameters:
        I2Cwrapper: Wrapper for I2C communication.
        crystalFreq (int): Frequnecy of the crystal oscillator. Defaults to PLLReg.CRYSTAL_FREQ_25MHZ.
    Reference:
        https://github.com/roseengineering/MicroPython-si5351.py
    """

    def __init__(self, I2CWrapper, crystalFreq = PLLReg.CRYSTAL_FREQ_25MHZ) -> None:
        """
        Initialize the PLLController.

        Parameters:
            I2CWrapper: Wrapper for I2C communication.
            crystalFreq (int): Frequency of the crystal oscialltor. Defaults to PLLReg.CRYSTAL_FREQ_25MHZ.

        
        """
        self.crystalFreq = crystalFreq
        self.plla_freq = 0
        self.communication = I2CWrapper

        clk_control_mapping = {
            0:  PLLReg.CLK0_CONTROL,
            1:  PLLReg.CLK1_CONTROL,
            2:  PLLReg.CLK2_CONTROL,
            3:  PLLReg.CLK3_CONTROL,
            4:  PLLReg.CLK4_CONTROL,
            5:  PLLReg.CLK5_CONTROL,
            6:  PLLReg.CLK6_CONTROL,
            7:  PLLReg.CLK7_CONTROL
        }
        self.clk_control_dict = clk_control_mapping

        multisynth_parameter1_mapping = {
            0: PLLReg.MULTISYNTH0_PARAMETERS_1,
            1: PLLReg.MULTISYNTH1_PARAMETERS_1,
            2: PLLReg.MULTISYNTH2_PARAMETERS_1,
            3: PLLReg.MULTISYNTH3_PARAMETERS_1,
            4: PLLReg.MULTISYNTH4_PARAMETERS_1,
            5: PLLReg.MULTISYNTH5_PARAMETERS_1,
            6: PLLReg.MULTISYNTH6_PARAMETERS_1
        }
        self.multisyn_p1 = multisynth_parameter1_mapping

        multisynth_parameter3_mapping = {
            0: PLLReg.MULTISYNTH0_PARAMETERS_3,
            1: PLLReg.MULTISYNTH1_PARAMETERS_3,
            2: PLLReg.MULTISYNTH2_PARAMETERS_3,
            3: PLLReg.MULTISYNTH3_PARAMETERS_3,
            4: PLLReg.MULTISYNTH4_PARAMETERS_3,
            5: PLLReg.MULTISYNTH5_PARAMETERS_3,
            6: PLLReg.MULTISYNTH6_PARAMETERS_3
        }
        self.multisyn_p3 = multisynth_parameter3_mapping


        #reset all clk outputs
        self.reg_write(PLLReg.OUTPUT_ENABLE_CONTROL, 0xFF)
        for clk_ctrl in range(0,8):
            self.reg_write(self.clk_control_dict.get(clk_ctrl), 0x80)

    def reg_write(self, address, data) -> None:
        """
        Write data to register.

        Parameter:
            address (int): Register address.
            data (int): Data to be written to the register.
        """

        self.communication.write_data(address, data)

    def reg_read(self, address: int) -> int:
        """
        Read data from a register.

        Parameters:
            address (int): Register address.

        Returns:
            int: Data read from the register.
        """
        data = self.communication.read_data(address, num_bytes=1)
        return data


    def set_frequency(self, target_frequency: int, output: int = 0, pll: int = PLLReg.PLL_A, mult: int = 32, roundit: bool = False) -> None:
        """
        Set the frequency of the PLL to the target_frequency.
        Decides if a frequency is below the minimum frequency. R divider needed for frequency lower then 500kHz down to 4kHz. 
        Checks if the desired frequency is less then 500kHz down to 4kHz. If so then use resistors.
        Initilaize the Feedback Multiplier.

        Parameters:
            target_frequency (int): Desired frequency for the PLL.
            output (int): Choose the output clock (clk0-clk7).
            pll (int): Choose which PLL (A or B) provides f_vco.
            roundit (bool): Rounds fraction division to nearest int value. Reduces jitter by loss of frequency precision.  
        """
        print(f"------------------------------------\n Set frequency to \n {target_frequency} \n")

        if (target_frequency >= 120_000_000):
            self.high_speed(target_frequency, output, pll, roundit)
            return
        
        mult = 36 # input clk multiplier must be between 15 and 90

        self.setup_feedbackMultisynth(pll, mult, 0, 1)

        freq = target_frequency
        r_div = PLLReg.R_DIV_1
        print("R not hitted")
        if (freq >= PLLReg.CLKOUT_MIN_FREQ and freq < PLLReg.CLKOUT_MIN_FREQ * 2):
            r_div = PLLReg.R_DIV_128
            freq *= 128
            print(f"R hitted: {r_div}")
        elif (freq >= PLLReg.CLKOUT_MIN_FREQ*2 and freq < PLLReg.CLKOUT_MIN_FREQ * 4):
            r_div = PLLReg.R_DIV_64
            freq *= 64
            print(f"R hitted: {r_div}")
        elif (freq >= PLLReg.CLKOUT_MIN_FREQ*4 and freq < PLLReg.CLKOUT_MIN_FREQ * 8):
            r_div = PLLReg.R_DIV_32
            freq *= 32
            print(f"R hitted: {r_div}")
        elif (freq >= PLLReg.CLKOUT_MIN_FREQ*8 and freq < PLLReg.CLKOUT_MIN_FREQ * 16):
            r_div = PLLReg.R_DIV_16
            freq *= 16
            print(f"R hitted: {r_div}")
        elif (freq >= PLLReg.CLKOUT_MIN_FREQ*16 and freq < PLLReg.CLKOUT_MIN_FREQ * 128):
            r_div = PLLReg.R_DIV_8
            freq *= 8
            print(f"R hitted: {r_div}")
        elif (freq >= PLLReg.CLKOUT_MIN_FREQ*32 and freq < PLLReg.CLKOUT_MIN_FREQ * 64):
            r_div = PLLReg.R_DIV_4
            freq *= 4
            print(f"R hitted: {r_div}")
        elif (freq >= PLLReg.CLKOUT_MIN_FREQ*64 and freq < PLLReg.CLKOUT_MIN_FREQ * 128):
            r_div = PLLReg.R_DIV_2
            freq *= 2
            print(f"R hitted: {r_div}")

        if pll == PLLReg.PLL_A:
            fvco = self.plla_freq
        else:
            fvco = self.pllb_freq

        print(f"fvco: {fvco}")
        print(f"freq: {freq}")

        if roundit == True:
            num = fvco % freq
            denom = freq
            value = num/denom
            num = 0
            denom = 1
            div = fvco//freq
            if value >= 0.5:
                div += 1
        else:            
            div = fvco // freq
            num = fvco % freq
            denom = freq

            if num == 0:
                denom = 1
            else:
                while denom > PLLReg.MULTISYNTH_C_MAX:
                    num //= 2
                    denom //= 2

        

        self.reset_pll()

        oe_ctrl = self.reg_read(PLLReg.OUTPUT_ENABLE_CONTROL)
        oe_cfg = oe_ctrl&(~(1<<output))
        print("oeb: {0:b}".format(oe_cfg))
        self.reg_write(PLLReg.OUTPUT_ENABLE_CONTROL, oe_cfg) #enable output clock

        self.setupMultisynth(output, div, num, denom)

        self.setupRdiv(output, r_div)

        

    def high_impedance(self, enable: bool) -> None:
        """
        Set the output of the PLL as high impedance if enable = True

        Parameters:
            enable (bool): Enable or disable high impedance.

        """
        self.reg_write(address=PLLReg.OUTPUT_ENABLE_CONTROL, data = 4 * enable) #maybe find a way to not have this 4 magic number


    def setup_feedbackMultisynth(self, pll: int, mult: int, num: int = 0, denom: int = 1) -> None:
        """
        Setup the feedback Multipath.

        Parameter:
            pll (int): Choose which PLL (A or B) provides f_vco.
            mult (int): PLL integer multiplier (must be between 15 and 90).
            num (int, optional): The 20-bit numerator for fractional output (0..1,048,575). Defaults to 0.
            denom (int, optional): The 20-bit numerator for fractional output (0..1,048,575). Defaults to 1.
        """
        print(f"\n Set feedback Multisynth \n")

        # Set the main PLL config registers
        print(f"mult: {mult}, num: {num}, denom: {denom}")

        P1 = 128 * mult + int(128.0 * num / denom) - 512
        P2 = 128 * num - denom * int(128.0 * num / denom)
        P3 = denom

        print(f"P1: {P1}")
        print(f"P2:  {P2}")
        print(f"P3:  {P3}")

        baseaddr = 26 if pll == PLLReg.PLL_A else 34 #Register 34 for use of PLLB

        self.reg_write(baseaddr,     (P3 & 0x0000FF00) >> 8)
        #isolate bits[15:8] and send it to the register
        self.reg_write(baseaddr + 1, (P3 & 0x000000FF))
        self.reg_write(baseaddr + 2, (P1 & 0x00030000) >> 16)
        self.reg_write(baseaddr + 3, (P1 & 0x0000FF00) >> 8)
        self.reg_write(baseaddr + 4, (P1 & 0x000000FF))
        self.reg_write(baseaddr + 5, ((P3 & 0x000F0000) >> 12) | ((P2 & 0x000F0000) >> 16) )
        #P3 should also be shifted by 12 ??
        self.reg_write(baseaddr + 6, (P2 & 0x0000FF00) >> 8)
        self.reg_write(baseaddr + 7, (P2 & 0x000000FF))

        fvco = int(self.crystalFreq*mult + float(num) /denom)
        if pll == PLLReg.PLL_A:
            self.plla_freq = fvco
        else:
            self.pllb_freq = fvco


    def setupMultisynth(self, output: int, div: int, num: int, denom: int) -> None:
        """
        Setup Multisynth divider, which  determines the output clock frequency based on the specified PLL input.

        Parameter:
            output (int): Output channel to choose.
            pll (int): PLL input source (now only PLLA since we don't use spread or VCXO).
            div (int): Integer divider for Multisynth output.
            num (int): The 20-bit numerator for fractional output (0..1,048,575). Set this to '0' for integer output.
            denom (int): The 20-bit numerator for fractional output (0..1,048,575). Set this to '0' for integer output.
        """
        print(f"\n Set setup Multisynth \n")

        print(f"divisor {div}")

        # Set the main PLL config registers
        P1 = 128 * div + int(128.0 * num / denom) - 512
        P2 = 128 * num - denom * int(128.0 * num / denom)
        P3 = denom

        print(f"P1: {P1}")
        print(f"P2:  {P2}")
        print(f"P3:  {P3}")
        print(f"divisor: {div}, num: {num}, denom: {denom}")

        baseaddr = self.multisyn_p3.get(output)

        print(f"baseaddr: {baseaddr}")

        self.reg_write(baseaddr,     (P3 & 0x0000FF00) >> 8)

        #isolate bits[15:8] and send it to the register
        self.reg_write(baseaddr + 1, (P3 & 0x000000FF))
        self.reg_write(baseaddr + 2, (P1 & 0x00030000) >> 16)
        self.reg_write(baseaddr + 3, (P1 & 0x0000FF00) >> 8)
        self.reg_write(baseaddr + 4, (P1 & 0x000000FF))
        self.reg_write(baseaddr + 5, ((P3 & 0x000F0000) >> 12) | ((P2 & 0x000F0000) >> 16) )

        #P3 should also be shifted by 12 ??
        self.reg_write(baseaddr + 6, (P2 & 0x0000FF00) >> 8)
        self.reg_write(baseaddr + 7, (P2 & 0x000000FF))

        #configure the clk control and enable output
        #8mA drive strength, MS0 as CLK0 source, Clock not inverted, power up

        clkControlReg = 0x0F
        if num == 0 : clkControlReg |= (1 << 6) #sets register in integer mode

        self.reg_write(self.clk_control_dict.get(output), clkControlReg) # here if condition for multiple clock output

    def high_speed(self, target_frequency: int, output: int, pll: int, roundit: bool) -> None:
        """
        Sets frequencies from 120Mhz to 200Mhz (overclock possible up to 300MHz)

         Parameters:
            target_frequency (int): Desired frequency for the PLL.
            output (int): Choose the output clock (clk0-clk7).
            pll (int): Choose which PLL (A or B) provides f_vco.
            roundit (bool): Rounds fraction division to nearest int value. Reduces jitter by loss of frequency precision.
        """

        self.setupMultisynth(output, 4, 0, 1) # set the output_Multisynth to the needed divisor 4

        self.setupRdiv(output, PLLReg.R_DIV_1)

        #set the Multisynth2 Parameter to Divide by 4 Enable
        divby4 = self.reg_read(self.multisyn_p1.get(output))
        print(f"data type from read is: {divby4}")
        divby4 |= 0xC #set the register value to Divide by 4
        self.reg_write(self.multisyn_p1.get(output), divby4)

        clkControlReg = self.reg_read(self.clk_control_dict.get(output))
        clkControlReg |= (1<<6) #set the control_setup to integer mode
        self.reg_write(self.clk_control_dict.get(output), clkControlReg)

        div = (target_frequency*4) // PLLReg.CRYSTAL_FREQ_25MHZ
        num = ((target_frequency*4) % PLLReg.CRYSTAL_FREQ_25MHZ)//1_000_000
        denom = PLLReg.CRYSTAL_FREQ_25MHZ//1_000_000          

        if roundit == True:
            value = num/denom
            num = 0
            denom = 1
            if value >= 0.5:
                div += 1

        self.reg_write(PLLReg.CRYSTAL_INTERNAL_LOAD_CAPACITANCE, PLLReg.CRYSTAL_LOAD_8PF)

        self.setup_feedbackMultisynth(pll, div, num, denom)

        self.reset_pll()

        oe_ctrl = self.reg_read(PLLReg.OUTPUT_ENABLE_CONTROL)
        oe_cfg = oe_ctrl&(~(1<<output))
        print("oeb: {0:b}".format(oe_cfg))
        self.reg_write(PLLReg.OUTPUT_ENABLE_CONTROL, oe_cfg) #enable output clock

        print("high speed frequency")
        return


    def setupRdiv(self, output: int = 2, div: int = 1) -> None:
        """
        Setup the R divisor, for only one outpupt clk

        Parameter:
            output (int): Output channel to choose.
            div (int): Interger divider.
        """
        print(f"output = {output}")
        Rreg = self.multisyn_p1.get(output)
        print(f"output number = {Rreg}")
        print(f"in register: {bin((div & 0x07) << 4)}")
        return self.reg_write(60, (div & 0x07) << 4)

    def enableOutput(self, enabled: bool) -> None:
        """
        Enables the selected output

        Parameter:
            enabled (bool): Whether the output should be enabled.
        """
        val = 0x00 if enabled else 0xFF
        self.reg_write(PLLReg.OUTPUT_ENABLE_CONTROL, val)

    def pll_stuck(self) -> int:
    # pylint: disable= line-too-long
        """
        Check Crystal Loss of Signal.

        Parameters:
            None

        Returns:
            int: 0 if valid crystal signal at the XA and XB Pins, 1 if loss of crystal signal detected.
        """
        print("checked stuck")
        status = (self.reg_read(0)>>3) & 0b1
        print(f"pllstuck_status: {status}")
        return status

    def reset_pll(self) -> None:
        """
        Resets the PLL.

        Parameters:
            None
        """

        #reset the PLL
        self.reg_write(PLLReg.PLL_RESET_REGISTER_177, (1<<7) | (1<<5))

    def powerdown(self, output: int) -> None:
        """
        Power down the output of the given clock.

        Parameters:
            output (int): Choose the output clock (clk0-clk7).
        """
        clkControlReg = self.reg_read(self.clk_control_dict.get(output))
        clkControlReg |= (1<<7) #write a one at specific bit
        self.reg_write(self.clk_control_dict.get(output), clkControlReg)

    def powerup(self, output: int) -> None:
        """
        Power up the output of the given clock.

        Parameters:
            output (int): Choose the output clock (clk0-clk7).
        """
        clkControlReg = self.reg_read(self.clk_control_dict.get(output))
        clkControlReg = clkControlReg & ~(1<<7) #write a zero at specific bit
        self.reg_write(self.clk_control_dict.get(output), clkControlReg)

    def invertclk(self, output: int) -> None:
        """
        Invert the output clock.
        
        Parameters:
            output (int): Choose the output clock (clk0-clk7).       
        """
        clkControlReg = self.reg_read(self.clk_control_dict.get(output))
        clkControlReg = clkControlReg ^ (1<<4) #flip bit by xor it
        self.reg_write(self.clk_control_dict.get(output), clkControlReg)

    def drive_strength(self, output: int, strength: int)-> None:
        """
        Set the drive strength for the given output.

        Parameters:
            output (int): Choose the output clock (clk0-clk7).
            strength (int): Choose the driving strength (2, 4, 6, 8mA).
        """
        clkControlReg = self.reg_read(self.clk_control_dict.get(output))
        if strength == 2: 
            clkControlReg = clkControlReg & ~(1<<0)
            clkControlReg = clkControlReg & ~(1<<1)  
        if strength == 4:
            clkControlReg = clkControlReg & ~(1<<1)
            clkControlReg |= (1<<0)
        if strength == 6:
            clkControlReg = clkControlReg & ~(1<<0)
            clkControlReg |= (1<<1)
        if strength == 8:
            clkControlReg |= (1<<0)
            clkControlReg |= (1<<1)
        self.reg_write(self.clk_control_dict.get(output), clkControlReg)

    def multisyn_source(self, output: int, pll: int):
        """
        Choose the MultiSynth Source.

        Parameters:
            output (int): Choose the output clock (clk0-clk7).
            pll (int): Choose which PLL (A or B) provides f_vco.
        """
        clkControlReg = self.reg_read(self.clk_control_dict.get(output))
        if pll == 0:
            clkControlReg = clkControlReg & ~(1<<5)
        if pll == 1: 
            clkControlReg |= (1<<5)
        self.reg_write(self.clk_control_dict.get(output), clkControlReg)

    def sweep_freq(self, start_freq: int, end_freq: int, step_size: int, period: int, output: int, pll: int, roundit: bool):
        """
        Function that sweeps a given frequency range with the given timestep.

        Parameters:
            start_freq (int): Starting point for the sweep.
            end_freq (int): End point of the sweep.
            step_size (int): Size between each step.
            period (int): Time between each step.
            output (int): Choose the output clock (clk0-clk7).
            pll (int): Choose which PLL (A or B) provides f_vco.
            roundit (bool): Rounds fraction division to nearest int value. Reduces jitter by loss of frequency precision.
        """
        for i in range(start_freq, end_freq+step_size, step_size):
            self.set_frequency(i, output, pll, 32 , roundit)
            sleep(period/1000)

    def hopping_freq(self, freq_array: list, amount: int, period: int, output: int, pll: int, roundit: bool) -> None:
        """
        Function that can be used to hop between frequency that are provided in freq_array

        Parameters:
        - freq_array (int): Array containing the frequencies to hop through.
        - amount (int): How often to itterate through the freq_array.
        - period (int): Time between each hop.
        - output (int):  Choose the output clock (clk0-clk7).
        - pll (int): Choose which PLL (A or B) provides f_vco.
        - roundit (bool): Rounds fraction division to nearest int value. Reduces jitter by loss of frequency precision.
        """
        length = len(freq_array)
        index = 0
        a = 0
        while a < amount:
            i = freq_array[index]
            self.set_frequency(i, output, pll, 32, roundit = roundit)
            sleep(period/1000)
            index = (index+1)%length
            a += 1

class FrequencyIterate:
    """
    Iterator for iterating over frequencies using PLLController.

    Attributes:
        current (int): Current frequency.

    Parameters:
        start_freq (int): Starting frequency.
        end_freq (int): Ending frequency.
        step_size (int): Size of each step.
        output (int): Output channel.
        pll (int): PLL input source.
        roundit (bool): Optional, rounds fractional division. Defaults to False.
    """
    def __init__(self, start_freq: int, end_freq: int, step_size: int, output: int, pll: int, roundit: bool = False) -> None:
        """
        Initialize the FrequencyIterate object.

        Parameters:
            start_freq (int): Starting frequency.
            end_freq (int): Ending frequency.
            step_size (int): Size of each step.
            output (int): Output channel.
            pll (int): PLL input source.
            roundit (bool): Optional
        """
        self.pll_controller = PLLController(I2CWrapper)
        self.current = start_freq
        self.end_freq = end_freq
        self.step_size = step_size
        self.output = output
        self.pll = pll
        self.pll_controller.set_frequency(self.current, self.output, self.pll, roundit = roundit)
    
    def __iter__(self) -> None:
        """
        Returns the iteratir object itself.
        """
        return self
    
    def __next__(self) -> None:
        """
        Returns the next item in the sequence.
        """
        self.current += step_size
        self.pll_controller.set_frequency(self.current, self.output, self.pll, roundit = roundit)
        if self.current < self.end_freq:
            return self.current
        raise StopIteration
    

if __name__ == "__main__":
    # Example usage of the I2CWrapper and PLLController classes
    roundit = False

    # Set the PLL frequency
    target_frequency = 300_000  # Example frequency in Hz
    #pll_controller.set_frequency(target_frequency, 2, PLLReg.PLL_A, roundit)
    #pll_controller.set_frequency(target_frequency*4, 2, PLLReg.PLL_B, roundit)

    freq_array = [31_000, 33_000]

    start_freq = 120_000_000
    end_freq = 150_000_000
    step_size = 5_000_000
    period = 2000
    output = 2
    pll = PLLReg.PLL_A
    amount = 100

    # iterator = FrequencyIterate(start_freq, end_freq, step_size, output, pll)
    # myiter = iter(iterator)
    # next(myiter)
    # sleep(2000)
    # print("next")
    # next(myiter)
    # sleep(2000)
    # print("next")
    # next(myiter)

    #pll_controller.invertclk(output)    
    #pll_controller.powerdown(output)
    #pll_controller.powerup(output)

    #pll_controller.hopping_freq(freq_array, amount, period, output, pll, roundit)

    #pll_controller.sweep_freq(start_freq, end_freq, step_size, period, output, pll, roundit)