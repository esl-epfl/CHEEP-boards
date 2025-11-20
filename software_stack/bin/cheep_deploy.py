#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from logging import Formatter, StreamHandler, getLogger, DEBUG, ERROR
from sys import modules, stderr
from traceback import format_exc
from pyftdi import FtdiLogger
from pyftdi.ftdi import Ftdi
from pyftdi.i2c import I2cController, I2cNackError
from pyftdi.misc import add_custom_devices

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../python/")
import cheep

def main():
    """Entry point."""
    debug = False
    try:
        argparser = ArgumentParser(description=modules[__name__].__doc__)
        argparser.add_argument('device', nargs='?', default='ftdi:///?',
                               help='serial port device name')
        argparser.add_argument('-C', '--chewing_gum', default=1, type=int, help='Chewing gum to program. Default = 1')
        hex2int=lambda x: int(x,0)
        for i in range(32):
            argparser.add_argument("-w{}".format(i), type=hex2int,help="Value of 32 bit word {} at address 0x{:02x}".format(i,i*4))
        argparser.add_argument('-P', '--vidpid', action='append',
                               help='specify a custom VID:PID device ID, '
                                    'may be repeated')
        argparser.add_argument('-v', '--verbose', action='count', default=0,
                               help='increase verbosity')
        argparser.add_argument('-d', '--debug', action='store_true',
                               help='enable debug mode')
        args = argparser.parse_args()
        debug = args.debug

        if not args.device:
            argparser.error('Serial device not specified')

        loglevel = max(DEBUG, ERROR - (10 * args.verbose))
        loglevel = min(ERROR, loglevel)
        if debug:
            formatter = Formatter('%(asctime)s.%(msecs)03d %(name)-20s '
                                  '%(message)s', '%H:%M:%S')
        else:
            formatter = Formatter('%(message)s')
        FtdiLogger.log.addHandler(StreamHandler(stderr))
        FtdiLogger.set_formatter(formatter)
        FtdiLogger.set_level(loglevel)

        try:
            add_custom_devices(Ftdi, args.vidpid, force_hex=True)
        except ValueError as exc:
            argparser.error(str(exc))

        i2c = I2cController()
        cb = cheep.CheepBoard(i2c)
        i2c.set_retry_count(1)
        i2c.configure(args.device)
        cb.set_i2c_mode()
        eeprom = cb.get_chewing_gum(args.chewing_gum)
        for i in range(32):
            id = "w{}".format(i)
            val = vars(args)[id]
            if val != None:
                eeprom[i]=val
    except (ImportError, IOError, NotImplementedError, ValueError) as exc:
        print('\nError: %s' % exc, file=stderr)
        if debug:
            print(format_exc(chain=False), file=stderr)
        exit(1)
    except KeyboardInterrupt:
        exit(2)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(str(exc), file=stderr)
