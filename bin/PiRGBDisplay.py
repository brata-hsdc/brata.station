#!python
#
#   File: PiRGBDisplay.py
# Author: Ellery Chan
#  Email: ellery@precisionlightworks.com
#   Date: 6-Feb-2010
#
#   Desc: An encapsulation of an OpenFlight file with some methods for
#         examining and manipulating it.
#
#   Note: Requires Adafruit_Python_CharLCD library.  The Python code for
#         Adafruit's Character LCDs on the Pi is available on Github at
#         https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code
#------------------------------------------------------------------------------

import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), os.pardir))
from station.Adafruit_CharLCDPlate import Adafruit_CharLCDPlate


#--------------------------------------------------------
class LcdRgbDisplay(object):
    ''' Drive Adafruit RGB LCD Pi Plate display.
    
        Notes:
        1.  The display can buffer a longer message than 16-chars per line, so
            you can send it a longer message, and then scroll it.
        2.  The cursor will blink autonomously.  All other animation must be
            driven by code.
    '''
    DISP_WIDTH  = 16
    DISP_HEIGHT =  2
    
    PRESSED = 1
    RELEASED = -1
    NEXT_STATE = (0, 1, 0, 3, 2, 3, 0, 3)
    OUTPUT     = (0, 0, 0, PRESSED, 0, 0, RELEASED, 0)
    NUM_STATES = len(NEXT_STATE)
    NUM_BUTTONS = 5
    BUTTONS = (Adafruit_CharLCDPlate.SELECT, Adafruit_CharLCDPlate.RIGHT, Adafruit_CharLCDPlate.DOWN, Adafruit_CharLCDPlate.UP, Adafruit_CharLCDPlate.LEFT)
    BUTTON_NAMES = ("SELECT", "RIGHT", "DOWN", "UP", "LEFT")
    DEBOUNCE_INTERVAL = 0.05 # sec.  (= sampling rate of 20 Hz)
    
    COLORS = {"BLACK":   (0.0, 0.0, 0.0), # backlight off
              "RED":     (1.0, 0.0, 0.0),
              "GREEN":   (0.0, 1.0, 0.0),
              "BLUE":    (0.0, 0.0, 1.0),
              "CYAN":    (0.0, 1.0, 1.0),
              "MAGENTA": (1.0, 0.0, 1.0),
              "YELLOW":  (1.0, 1.0, 0.0),
              "WHITE":   (1.0, 1.0, 1.0),
              }
    
    def __init__(self):
        self._lcd = Adafruit_CharLCDPlate()  # initialize the hardware
        self._donePolling = False # for breaking out of polling loop
    
        self._lcd.leftToRight()
        self._lcd.noAutoscroll()
        
    def clear(self):
        self._lcd.clear()
        
    def setBgColor(self, color):
        ''' Set the display background color to [rgb].  The color component
            values are in the range 0.0 .. 1.0.
        '''
        self._lcd.backlight(*self.COLORS[color])
    
    def setText(self, text):
        ''' Display text.  \n will jump to the next line of the display.
        '''
        self._lcd.message(text)
    
    def isPressed(self, button):
        return self._lcd.is_pressed(button)
    
    def pollButtons(self):
        ''' Poll the input buttons.  Does a little debounce.  Not sure if it is
            necessary.
            
            Button state transitions:
        
                                     |       button input
                current state        |           0         |        1
            ------------------------------------------------------------------
                 0 (released)        |   0                 |  1                
                 1 (maybe pressed)   |   0                 |  3 (emit PRESSED) 
                 3 (pressed)         |   2                 |  3
                 2 (maybe released)  |   0 (emit RELEASED) |  3
        '''
        
        buttonStates = [0, 0, 0, 0, 0]
        
        self._donePolling = False
        while not self._donePolling:
            # Sample the current state of all buttons
            buttonInputs = map(self._lcd.is_pressed, self.BUTTONS)
            
            # Convert prevState, input to an index = 2*state + input
            buttonStateTransitions = map(lambda s,i: 2*s+i, buttonStates, buttonInputs)
            
            # Use the transition to lookup the next state
            buttonStates = [self.NEXT_STATE[i] for i in buttonStateTransitions]
            
            # Use the transition to lookup the output value
            outputs = [self.OUTPUT[i] for i in buttonStateTransitions]
            
            # Make a list of buttons that changed to PRESSED and a list of buttons
            # that changed to RELEASED
            edges = ([i for i in range(self.NUM_BUTTONS) if outputs[i] == self.PRESSED],
                     [i for i in range(self.NUM_BUTTONS) if outputs[i] == self.RELEASED])
            
            # Report the buttons that changed
            if len(edges[0]):
                self.deliverButtonPressEvents(edges[0])
            if len(edges[1]):
                self.deliverButtonReleaseEvents(edges[1])
                
            # Be nice to the CPU
            time.sleep(0.05)
        
    def deliverButtonPressEvents(self, buttons):
        ''' Sample button press event hook.
            Hold down SELECT and RIGHT buttons to return from polling.
        '''
        print "Pressed:", [self.BUTTON_NAMES[i] for i in buttons]
        if self.isPressed(Adafruit_CharLCDPlate.SELECT) and self.isPressed(Adafruit_CharLCDPlate.RIGHT):
            self.quitPolling()

    def deliverButtonReleaseEvents(self, buttons):
        ''' Sample button release event hook.
        '''	
        print "Released:", [self.BUTTON_NAMES[i] for i in buttons]
    
    def quitPolling(self):
        ''' Break out of polling loop and return from pollButtons()
        '''
        self._donePolling = True

#------------------------------------------------------------------------------
if __name__ == '__main__':
    lcd = LcdRgbDisplay()

    lcd.setBgColor("GREEN")
    lcd.setText("** Pi Display **\n    12:34:56")
    lcd.pollButtons() # hold SELECT and RIGHT to quit
