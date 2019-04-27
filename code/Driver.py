import RPi.GPIO as GPIO
import spiUtilsExt as su
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import fluidsynth
from threading import Thread

#setup global Fluid Synth object
fs = fluidsynth.Synth()
fs.start("alsa")
sfid = fs.sfload("R-marmba.sf2")
fs.program_select(0, sfid, 0, 0)

#constants
NOTES = [24, 26, 28, 29, 31, 33, 35, 36]
instruments = { 17: "R-marmba.sf2", 16: "Craftsynth.sf2", 13: "Grandpno.sf2" }

#misc
plt.ioff()

class Driver:
    
    #
    # Driver Constructor: initializes all instance varables and sets up GPIO settings
    #
    def __init__(self):
        #Instantiate all instance variables
        self.keyChannels = [x for x in range(0, 8)]
        self.potChannel = 0     
        self.previous = [0] * 8;
        self.hit = False
        self.buttonPin = 22; 
        self.ledPins = [(25 - x) for x in range(8)]
        self.octave = 0;
        #Set up GPIO
        GPIO.setmode(GPIO.BCM)
        for pin in self.ledPins:
            GPIO.setup(pin, GPIO.OUT)
        for pin in self.ledPins:
            GPIO.output(pin, False)
        for pin in instruments:
            GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) 
    
    #
    # Plays the the fluid synth note given myArgs. Also flashes LED
    # @param: int myArgs - argument defined by the threading class (note to be played 0-7)
    #
    def threadedPlayNote(self, myArgs):
        #get the note being played depending on the octave
        note = NOTES[myArgs] + (12*self.octave)
        #play note and flash LED
        fs.noteon(0, note, 30)
        GPIO.output(self.ledPins[myArgs], True)
        time.sleep(0.1)
        GPIO.output(self.ledPins[myArgs], False)
        time.sleep(0.9)
        fs.noteoff(0, myArgs)
        time.sleep(1)
 
        
    #
    # Returns a sample of all 8 keys as an average of a given number of samples
    # @param: int samples
    # @return: list of average analog values from each Force Sensitive Resistor
    #
    def sampleKeys(self, samples):
        data = [0] * 8  #list to store data for each key
        #For every sample
        for sample in range(samples):
            #for every key
            for key in self.keyChannels:
                data[key] += (su.readADC(0, key)) #add one sample to the key's data
        #Return list of averages for each key
        return [x / samples for x in data]
    
    #
    # Returns a sample of one analog reading from the potentiometer
    # @return: potentiometer analog value
    #
    def samplePot(self):
        return su.readADC(1, self.potChannel)
    
    #
    # Plays notes, given the current sample of current and previous values from thec Force Sensitve Resistors
    # @param: List notes - sample of all Force Sensitive Resistors from the sampleKeys method
    #
    def playNotes(self, notes):
        #for every note
        for i in range(len(notes)):
            current = notes[i]
            if(self.previous[i] <= 1000 and current > 1000):
                self.hit = True
            elif(self.previous[i] <= 1000 and current <= 1000):
                self.hit = False
            elif(self.previous[i] > 1000 and current > 1000):
                self.hit = False
            self.previous[i] = current
            if(self.hit):
                print("Hit!")
                thread = Thread(target = self.threadedPlayNote, args = ([i]))
                thread.daemon = True
                thread.start()
            
    #
    # Main function to play marimba. Loops until quit by keyboard interrupt. 
    # Checks instrument button pressed, octave value, sampels keys, samples note and plays notes
    #
    def play(self):
        print("play")
        while True:
            for pin in instruments:
                if GPIO.input(pin):
                    sfid = fs.sfload(instruments[pin])
                    fs.program_select(0, sfid, 0, 0)
                    
            #Check all input setting sensors
            self.octave = (int) (self.samplePot() / 170) #check octave with potentiometer, mapped 1-1023 --> 0 - 6
            
            notes = self.sampleKeys(5)
            self.playNotes(notes)
    
    #
    # Runs startup sequence for LED's
    #
    def ledStartup(self):
        for i in range(3):
            for pin in self.ledPins:
                GPIO.output(pin, True)
                time.sleep(0.12 - 0.04*i)
            for pin in self.ledPins:
                GPIO.output(pin, False)
                time.sleep(0.12 - 0.04*i)
                
    def calculateThreshold(self):
        #Run user prompts
        print("Calculate Threshold...")
        print("Tap 1st key consistently until prompted to stop")
        for i in range(3):
            print("..." + str(3 - i))
            time.sleep(1)
        print("GO!")
        #collect data
        dataList = []
        timeList = []
        #collect for 6 seconds
        timeEnd = time.time() + 6
        while time.time() < timeEnd:
            timeList.append(time.time() - timeEnd + 6)
            dataList.append(su.readADC(0, self.keyChannels[0]))
        print("STOP!")
        print("Exporting plot...")
        dataNp = np.array(dataList)
        timeNp = np.array(timeList)
        #export plot
        fig = plt.figure()
        plt.plot(timeNp, dataNp)
        plt.title('Force Sensitive Resistor Threshold Data')
        plt.xlabel('Seconds')
        plt.ylabel('FSR Analog Value')
        plt.savefig("plot-2.png")
        plt.close(fig)
        print("done")
            
        
    
if __name__ == "__main__":
    try:
        #Run initialization graphic
        print("Initializing...")
        time.sleep(1)
        driver = Driver()
        driver.calculateThreshold()
        driver.ledStartup()
        driver.play()
        


    except(KeyboardInterrupt, SystemExit):
        print("Interrupt!")

    finally:
        print("Done!")
        GPIO.cleanup();  # close GPIO
        fs.delete()