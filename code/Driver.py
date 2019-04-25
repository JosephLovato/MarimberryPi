import RPi.GPIO as GPIO
import spiUtilsExt as su
import time
import numpy as np
import fluidsynth
from threading import Thread

#setup global Fluid Synth object
fs = fluidsynth.Synth()
fs.start("alsa")
sfid = fs.sfload("R-marmba.sf2")
fs.program_select(0, sfid, 0, 0)

#constants
NOTES = [24, 26, 28, 29, 31, 33, 35, 36]

class Driver:
    
    def __init__(self):
        #Instantiate all instance variables
        self.keyChannels = [x for x in range(0, 8)]
        self.potChannel = 0     
        self.previous = [0] * 8;
        self.hit = False
        self.buttonPin = 22; 
        self.ledPins = [x for x in range(18, 25)]
        self.octave = 0;
        #Set up GPIO
        GPIO.setmode(GPIO.BCM) #set up pins
        for pin in self.ledPins:
            GPIO.setup(pin, GPIO.OUT)
        GPIO.setup(self.buttonPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #set up button as input
            
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
    # @return: list averages
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
    
    def samplePot(self):
        return su.readADC(1, self.potChannel)
    
    
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
            
           
    def play(self):
        while True:
            #Check all input setting sensors
            self.octave = (int) (self.samplePot() / 170)
            notes = self.sampleKeys(5)
            self.playNotes(notes)
        
        
    
if __name__ == "__main__":
    try:
        #Run initialization graphic
        print("Initializing...")
        time.sleep(1)
        driver = Driver()
        driver.play()
        


    except(KeyboardInterrupt, SystemExit):
        print("Interrupt!")

    finally:
        print("Done!")
        GPIO.cleanup();  # close GPIO
        fs.delete()