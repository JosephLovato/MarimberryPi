# MarimberryPi
Project Files for the MarimberryPi project. CSCI250 @ Colorado School of Mines

MarimberryPi/code: code base

MarimberryPi/misc: miscellaneous data

MarimberryPi/resources: various resources for project

THe MarimberryPi project is a sensor systems based project built to provide a midi interface for hittable-keys with a raspberry pi. 

## Hardware Required:
- Raspberry Pi 3
- (2) MCP3008 - 8-Channel 10-Bit ADC With SPI Interface (https://www.adafruit.com/product/856)
- Up to 16 Force Sensitive Resistors (https://www.sparkfun.com/products/9375)
- Up to 16 LEDs
- 3 buttons
- 330 Ω Resistors
- 1 Ω Resistors
- 1 Potentiometer

Highly Recommened:
- Jumper Wires
- Flat jumping wires

## Dependencies
- FluidSynth [Version 1.1.6-4] http://www.fluidsynth.org/ 
- pyfluidsynth [Version 1.2.5| https://github.com/nwhitehead/pyfluidsynth (python bindings for FluidSynth)
- RPi.GPIO [Version 0.6.5] https://pypi.org/project/RPi.GPIO/
- numpy [Version 1:1.12.1-3] https://www.numpy.org/
- matplotlib [Version 2.0.0+dfsg1-2] https://matplotlib.org/

## Setup
To begin, download all dependencies from above. Once hardware is setup, navigate to the MarimberryPi/code. Simply run:

`python3 Driver.py`

3 SF2 sound fonts are included. To change these, visit a sound font library and make sure to download only .sf2 files. Then, change the file name in Drive.py
