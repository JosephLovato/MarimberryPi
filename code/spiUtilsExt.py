# Code Adapated from https://pimylifeup.com/raspberry-pi-adc/
#
# MarimberryPi: spiUtilsExt.py
# Used to read in Analog values from 2 MCP3008 ADCs
#
# Joey Lovato, Kara McDonough
# 4/16/19
#

import spidev
import time

def readADC(chip, channel):
    if chip > 1 or chip < 0:
        return -1
    if channel > 7 or channel < 0:
        return -1
    spi = spidev.SpiDev()
    spi.open(0, chip)
    spi.max_speed_hz = int(1350000)
    r = spi.xfer2([1, 8 + channel << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    spi.close()
    return data