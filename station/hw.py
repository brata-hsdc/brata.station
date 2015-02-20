# ------------------------------------------------------------------------------
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ------------------------------------------------------------------------------
"""
TODO module description
"""

import datetime
import logging
import logging.handlers
# TODO Is UnresolvedImport needed? hw.py should not be enabled on a non-Pi; same for LCD below.
import pibrella  # @UnresolvedImport when not on R-Pi
import signal
import sys
from time import sleep
from threading import Thread
from threading import Event
import traceback
import math
import operator
import Queue

import Adafruit_CharLCD as LCD    # @UnresolvedImport when not on R-Pi
#tried various installs finally got working but seems too complex
import sys
sys.path.append('/opt/designchallenge2015/Adafruit-Raspberry-Pi-Python-Code/Adafruit_PWM_Servo_Driver')
from Adafruit_PWM_Servo_Driver import PWM

from interfaces import IDisplay
from interfaces import ILed
from interfaces import IPushButtonMonitor
from interfaces import IVibrationMotor
from interfaces import IBuzzer
from interfaces import IInput
from interfaces import IUrgencyLed

from station.util import Config
from station.util import PushButton

from mido import MidiFile
import os
from enum import Enum


# ------------------------------------------------------------------------------
class Display(IDisplay):
    """
    TODO class comment
    """

    COLORS = {"BLACK":   (0.0, 0.0, 0.0), # backlight off
              "RED":     (1.0, 0.0, 0.0),
              "GREEN":   (0.0, 1.0, 0.0),
              "BLUE":    (0.0, 0.0, 1.0),
              "CYAN":    (0.0, 1.0, 1.0),
              "MAGENTA": (1.0, 0.0, 1.0),
              "YELLOW":  (1.0, 1.0, 0.0),
              "WHITE":   (1.0, 1.0, 1.0),
              }


    # --------------------------------------------------------------------------
    def __init__(self,
                 config):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Constructing display')

        self._line1Text = ''
        self._line2Text = ''
        self._lineWidth = config.lineWidth
        logger.debug('Display line width: {} chars'.format(self._lineWidth))
        self._lcd = LCD.Adafruit_CharLCDPlate()


    # --------------------------------------------------------------------------
    def __enter__(self):
        """ Called when the context of a "with" statement is entered
        Returns:
            Reference to self
        """
        logger.debug('Entering display')
        return self


    # --------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        """ Called when the context of a "with" statement is exited

        Clears the display text and hides the cursor.  The backlight is left in its
        current state.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Exiting display')
        self.setText('')
        self.showCursor(False) # must call after setText(), which displays the cursor


    # --------------------------------------------------------------------------
    def lineWidth(self):
        """ Returns: the number of columns in a line of the display.
        """
        return self._lineWidth


    # --------------------------------------------------------------------------
    def setBgColor(self,
                   color):
        ''' Set the display background color to the specified color.
        
        Sets the display backlight to the color specified by the color name parameter.
        The valid color names are "BLACK", "RED", "GREEN", "BLUE", "CYAN", "YELLOW",
        "MAGENTA", "WHITE".

        Raises:
            KeyError if color is not one of the valid color string values.
        '''
        self._lcd.set_color(*self.COLORS[color])
    

    # --------------------------------------------------------------------------
    def setLine1Text(self,
                     text):
        """Sets the text for line 1 of the display.

        Sets the text for line 1 of the display. If the text is too long to fit
        on the display, then the text scrolls over time.

        Args:
            text (string): The text to display.
        """
        self._line1Text = "{:<{width}}".format(text, width=self._lineWidth)
        #logger.debug('Setting Line 1 text to "%s"' % self._line1Text)
        self._refreshDisplay()


    # --------------------------------------------------------------------------
    def setLine2Text(self,
                     text):
        """Sets the text for line 2 of the display.

        Sets the text for line 2 of the display. If the text is too long to fit
        on the display, then the text scrolls over time.

        Args:
            text (string): The text to display.
        """
        self._line2Text = "{:<{width}}".format(text, width=self._lineWidth)
        #logger.debug('Setting Line 2 text to "%s"' % self._line2Text)
        self._refreshDisplay()


    # --------------------------------------------------------------------------
    def setText(self,
                text):
        """ Sets the text for the entire display.

        Directly sets the text for the display. Multiple lines can be provided
        at once by separating with a '\n' character.  The first two lines will
        be displayed.  Other lines will be discarded.

        Args:
            text (string): The text to display.
        """
        lines = (text+'\n').split('\n')
        self.setLine1Text(lines[0])
        self.setLine2Text(lines[1])
        self._refreshDisplay()


    # --------------------------------------------------------------------------
    def showCursor(self, show=True):
        """ Shows or hides the cursor.
        
        Make the cursor visible if show is True.  Otherwise, make the cursor
        invisible.
        """
        #logger.debug('Setting show cursor value to %s' % (show))
        self._lcd.blink(show)
        self._lcd.show_cursor(show)

        
    # --------------------------------------------------------------------------
    def setCursor(self, row=0, col=0):
        """ Sets the position of the cursor and makes it visible.
        """
        #logger.debug('Setting cursor position to (r=%s, c=%s)' % (row, col))
        self._lcd.set_cursor(col, row)
        self.showCursor()

        
    # --------------------------------------------------------------------------
    def _refreshDisplay(self):
        """ Sends text to the display

        Sends or resends the text stored in _line1Text and _line2Text to
        the display.  Also causes the cursor to be displayed.
        """
        self.setCursor(0, 0)
        self._lcd.message(self._line1Text + '\n' + self._line2Text)
        #logger.debug('Display now reads "%s"[br]"%s"' % (self._line1Text, self._line2Text))

# ------------------------------------------------------------------------------
class LedType(Enum):
    pibrella = 1
    adafruit = 2

class I2CLedWorkerThreadCmd():
    def __init__(self, startPercentageOn, endPercentageOn, durationInSeconds):
        # Note duration of 0 = indefinitely
        self.startPercentageOn = startPercentageOn
        self.endPercentageOn = endPercentageOn
        self.durationInSeconds = durationInSeconds

class I2CLedWorkerThread(Thread):
    """ A worker thread that controls an led light over a period of time.

        This is done this way to exploit the queue waiting which takes less 
        cpu time than sleeping to help avoid thrashing with many of these
        running concurrently.  It was adapted form the public domain work:
        http://eli.thegreenplace.net/2011/12/27/python-threads-communication-and-stopping

        TaskMaster must support the following:
        setLed(newPercentBrightness) to allow reach back to control light level
        cmds which is a Queue of I2CLedWorkerThreadCmd objects.
        The thread has a fixed periodicity which once hit will start the 
        next available command if no new command it will keep doing what it
        was doing.

        Ask the thread to stop by calling its join() method to clean up before
        exiting the application.  __exit__ should be called to catch this but
        currently it appears to not always be called.
    """
    def __init__(self, taskMaster):
        super(I2CLedWorkerThread, self).__init__()
        self._taskMaster = taskMaster
        # init variables for supporting dynamic lighting changes
        self._currentBrightness = 0
        self._endBrightness = 0
        self._stepsRemaining = 0
        # Set minimum time step between changes
        self._TIME_TICK = 0.001 # note 0.0001 is possible but CPU thrashes
        self._delta = self._TIME_TICK
        self._isChanging = False

        self.stoprequest = Event()

    def run(self):
        # As long as we weren't asked to stop, try to take new tasks from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.
        # Also, 'get' is given a timeout, so stoprequest is always checked,
        # even if there's nothing in the queue.
        while not self.stoprequest.isSet():
            try:
                nextCmd = self._taskMaster.cmds.get(True,self._TIME_TICK)
                # if no cmd keep doing what you were doing even if was nothing
                # by taking the exception path on the timeout
                # otherwise process the new command and reset the thread state
                self._isChanging = True
                self._currentBrightness = nextCmd.startPercentageOn / 100.0
                self._endBrightness = nextCmd.endPercentageOn / 100.0
                if nextCmd.durationInSeconds > self._TIME_TICK:
                    # note early python ceil could return float
                    self._stepsRemaining = int(math.ceil(nextCmd.durationInSeconds/self._TIME_TICK))
                    self._delta = (self._endBrightness - self._currentBrightness) / self._stepsRemaining
                elif nextCmd.durationInSeconds == 0:
                    self._stepsRemaining = 0
                    self._currentBrightness = self._endBrightness
                    self._isChanging = False
                else:
                    self._stepsRemaining = 1
                self._taskMaster.setLed(self._currentBrightness)
            except Queue.Empty:
                if self._isChanging:
                    if self._stepsRemaining > 1:
                        self._currentBrightness = self._currentBrightness + self._delta
                    elif 1 == self._stepsRemaining:
                        self._currentBrightness = self._endBrightness
                        # Reached the base case for fade so terminate it
                        self._isChanging = False
                        # TODO handle if pulsing
                        # Reset values for next pulse cycle then treat like fade

                    self._stepsRemaining = self._stepsRemaining - 1 
                    #self._pwm.setPWM(self._chan, 0, self._percentOnAsDecimalToGammaLevel(self._currentBrightness))
                    self._taskMaster.setLed(self._currentBrightness)
                continue

    def join(self, timeout=None):
        self.stoprequest.set()
        super(I2CLedWorkerThread, self).join(timeout)

class PibrellaLedFacade():
    def __init__(self, chan, val, step, enabled):
        self._val = int(math.floor(val)) # just in case is float and using 2.x
        self._step = step # TODO so we really don't honor this right now
        self._chan = chan
        self.enabled = enabled
        self._gamma = []
        self._MAX_LEVEL = self._val
        for i in range(self._MAX_LEVEL+1):
            self._gamma.append(int(pow(i/(1.0*self._MAX_LEVEL), 2.8)*self._MAX_LEVEL))
        initialValue = self._gamma[0]
        if self.enabled:
            initialValue = self._gamma[self._val]
        self._pwm = PWM(0x40, debug=False)
        self._pwm.setPWMFreq(400)
        self._pwm.setPWM(self._chan, 0, initialValue)

        self._isRunning = False
        self.cmds = Queue.Queue()
        #self._thread = I2CLedWorkerThread(self)
        #self._thread.start()

    def __exit__(self, type, value, traceback):
        self.off()
        if self._isRunning:
            # stop was not called first so try to clean up
            self.stop()

    # --------------------------------------------------------------------------
    def stop(self):
        """This MUST be called when your program is shutting down.

        TODO Detailed multi-line description if
        necessary.
        This cleans up all of the thread processing and leaves the led off.
        Note once stop is called on and off will work but fade and pulse 
        will no longer work.
        TODO redo this threading model to allow cleaner working thread.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.info('Stopping LED.')
        self.off()
        self._isRunning = False
      #  self._thread.join()

    def _percentOnAsDecimalToGammaLevel(self, valueFromZeroToOne):
        # note use of int is for earlier python when floor could return float
        gammaLevel = int(math.floor(self._MAX_LEVEL * valueFromZeroToOne))
        gammaValue = 0
        if gammaLevel >= 0 and gammaLevel <= self._MAX_LEVEL:
            gammaValue = self._gamma[gammaLevel]
        return gammaValue

    def setLed(self, newPercentBrightness):
        self._pwm.setPWM(self._chan, 0, self._percentOnAsDecimalToGammaLevel(newPercentBrightness))

    def on(self):
        #nextCmd = I2CLedWorkerThreadCmd(100,100,0)
        #self.cmds.put(nextCmd)
        self._val = self._MAX_LEVEL
        self.enabled = True
        self._pwm.setPWM(self._chan, 0, self._percentOnAsDecimalToGammaLevel(1))

    def off(self):
        #nextCmd = I2CLedWorkerThreadCmd(0,0,0)
        #self.cmds.put(nextCmd)
        self._val = 0
        self.enabled = False
        self._pwm.setPWM(self._chan, 0, self._percentOnAsDecimalToGammaLevel(0))

    def fade(self, startPercentageOn, endPercentageOn, durationInSeconds):
        #nextCmd = I2CLedWorkerThreadCmd(startPercentageOn, endPercentageOn, durationInSeconds)
        #self.cmds.put(nextCmd)
        self._pwm.setPWM(self._chan, 0, self._percentOnAsDecimalToGammaLevel(1))

    def pulse(self, fadeInTime, fadeOutTime, onTime, offTime):
        # TODO
        pass

    def decay(self):
        """ Decay from full brightness to off

        Each call updates the LED (if enabled) to go from full brightness to
        off in smooth steps. True is returned if the LED is still on (non-zero
        brightness). False is returned if the LED has decayed to off (zero)
        brightness.
        """
        if self.enabled:
            if self._val >= self._step:
                self._val = self._val - self._step
                self._pwm.setPWM(self._chan, 0, self._gamma[self._val])
                return True
            else:
                self._val = 0
                self._pwm.setPWM(self._chan, 0, self._gamma[self._val])
                self.enabled = False
                return False
        else:
            # The value should already be off so why keep setting it?
            #self._pwm.setPWM(self._chan, 0, self._gamma[0])
            return False

# ------------------------------------------------------------------------------
class Led(ILed):
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 name, 
                 config):
        """Initializes the LED class

        TODO Detailed multi-line description if
        necessary.

        Args:
            name (string): Name of this instance of the LED class. Example "Bob"
            config (Config): Configuration object for the LED class
        Returns:
            N/A
        Raises:
            N/A

        """
        self.Name = name
        self.FlashingOnDuration_s = 0.5
        self.FlashingOffDuration_s = 0.5
        
        # Store results of what type of LED we are controlling
        # default to pibrella
        self._LedType = LedType.pibrella
        if  hasattr(config, 'LedType'):
            if config.LedType.lower().startswith("adafruit"):
               self._LedType = LedType.adafruit

        if self._LedType == LedType.pibrella:
            self.outputPin = getattr(pibrella.light, config.OutputPin)
        else:
            # TODO verify channel is valid
            self.outputPin = PibrellaLedFacade(int(name), 4095, 64, False)

    def stop(self):
        if self._LedType == LedType.adafruit:
            self.outputPin.stop()

    # --------------------------------------------------------------------------
    def turnOn(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        #logger.debug('Set LED steady ON \"%s\".', self.Name)
        self.outputPin.on()

    # --------------------------------------------------------------------------
    def turnOff(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        #logger.debug('Set LED steady OFF \"%s\".', self.Name)
        self.outputPin.off()

    # --------------------------------------------------------------------------
    def setFlashing(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Set LED flashing \"%s (%s..%s)\".',
                     self.Name,
                     self.FlashingOnDuration_s,
                     self.FlashingOffDuration_s)
        
        # Pulse function, FadeInTime_s, FadeOutTime_s, OnTime_s, OffTime_s
        self.outputPin.pulse(0, 0, self.FlashingOnDuration_s, self.FlashingOffDuration_s)

    # --------------------------------------------------------------------------
    def fade(self, startPercentageOn, endPercentageOn, durationInSeconds):
        """ See interface definition
        """
        self.outputPin.fade(startPercentageOn, endPercentageOn, durationInSeconds)

    # --------------------------------------------------------------------------
    def decay(self):
        """ See interface definition
        """
        self.outputPin.decay()

# ------------------------------------------------------------------------------
class PushButtonMonitor(IPushButtonMonitor):
    """
    TODO class comment
    """
    
    PRESSED = 1
    RELEASED = -1
    NEXT_STATE = (0, 1, 0, 3, 2, 3, 0, 3)
    OUTPUT     = (0, 0, 0, PRESSED, 0, 0, RELEASED, 0)
    NUM_STATES = len(NEXT_STATE)
    BUTTONS = (LCD.SELECT, LCD.RIGHT, LCD.DOWN, LCD.UP, LCD.LEFT)
    NUM_BUTTONS = len(BUTTONS)
    BUTTON_NAMES = ("SELECT", "RIGHT", "DOWN", "UP", "LEFT")
    DEBOUNCE_INTERVAL = 0.05 # sec.  (= sampling rate of 20 Hz)

    # --------------------------------------------------------------------------
    def __init__(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Constructing push button monitor')
        
        self._device = None  # button interface device
        self._buttonStates = [0] * self.NUM_STATES  # last sampled state of each button
        self._debounceButtons = False  # perform software debounce
        
        self._pushButtons = {}
        self._listening = False
        self._timeToExit = False
        self._onTickCallback = None
        
        self._thread = Thread(target = self.run)
        self._thread.daemon = True
        self._thread.start()

    # --------------------------------------------------------------------------
    def setOnTickCallback(self, cb=None):
        """ Attach a callback that gets called once per iteration of the button polling loop.
        """
        self._onTickCallback = cb
        
    # --------------------------------------------------------------------------
    def setDevice(self, dev):
        """ Register the hardware device for the push buttons.
        """
        self._device = dev
        
    # --------------------------------------------------------------------------
    def __enter__(self):
        logger.debug('Entering push button monitor')
        return self

    # --------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Exiting push button monitor')
        self.stopListening()
        self._timeToExit = True
        self._thread.join()

    # --------------------------------------------------------------------------
    def startListening(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Starting listening for push button monitor')
        # TODO
        self._listening = True

    # --------------------------------------------------------------------------
    def stopListening(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Stopping listening for push button monitor')
        self._listening = False

    # --------------------------------------------------------------------------
    def registerPushButton(self,
                           name,
                           buttonPressHandler,
                           config):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        # TODO[BEGIN]
        keypress = config.HwKeyPress

        if keypress in self._pushButtons:
            logger.warning('Console key [%s] already registered to push button %s; redefining to register to push button %s' %
                           (keypress, self._pushButtons[keypress].Name, name))

        self._pushButtons[keypress] = PushButton(name, buttonPressHandler)

        logger.debug('Registered push button %s for key press [%s]' %
                     (name, keypress))
        # TODO[END]

    # --------------------------------------------------------------------------
    def pollPushButtons(self):
        """ Sample the current state of the push buttons, detect changes.
        
            Poll the input buttons.  Does a little debounce.  Not sure if it is
            necessary.
            
            Button state transitions:
        
                                     |       button input
                current state        |           0         |        1
            ------------------------------------------------------------------
                 0 (released)        |   0                 |  1                
                 1 (maybe pressed)   |   0                 |  3 (emit PRESSED) 
                 3 (pressed)         |   2                 |  3
                 2 (maybe released)  |   0 (emit RELEASED) |  3
        """
        if self._debounceButtons:
            # Sample the current state of all buttons
            buttonInputs = map(self._device.is_pressed, self.BUTTONS)
             
            # Convert prevState, input to an index = 2*state + input
            buttonStateTransitions = map(lambda s,i: 2*s+(1 if i else 0), self._buttonStates, buttonInputs)
                 
            # Use the transition to lookup the next state
            self._buttonStates = [self.NEXT_STATE[i] for i in buttonStateTransitions]
             
            # Use the transition to lookup the output value
            outputs = [self.OUTPUT[i] for i in buttonStateTransitions]
        else:
            outputs = map(self._device.is_pressed, self.BUTTONS)
            
        # Make a list of buttons that changed to PRESSED and a list of buttons
        # that changed to RELEASED
        edges = ([i for i in range(self.NUM_BUTTONS) if outputs[i] == self.PRESSED],
                 [i for i in range(self.NUM_BUTTONS) if outputs[i] == self.RELEASED])
        
        # Report the buttons that changed
        if len(edges[0]):
            self.deliverButtonPressEvents(edges[0])
        if len(edges[1]):
            self.deliverButtonReleaseEvents(edges[1])
        
    # --------------------------------------------------------------------------
    def deliverButtonPressEvents(self, buttons):
        """ Call the push callback for buttons that were pressed
        """
        for b in buttons:
            button = self._pushButtons[self.BUTTON_NAMES[b]]
            button.Handler(button.Name)
            
    # --------------------------------------------------------------------------
    def deliverButtonReleaseEvents(self, buttons):
        """ Call the push callback for buttons that were pressed
        There are no handlers defined for release events, so this method
        does nothing.
        """
        pass

    # --------------------------------------------------------------------------
    def onTick(self):
        """ Calls user-supplied callback for each iteration of the polling loop.
        
        Attach a custom callback by calling self.setOnTickCallback().
        """
        if self._onTickCallback:
            self._onTickCallback()
    
    # --------------------------------------------------------------------------
    def run(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
#         with NonBlockingConsole() as nbc:
        logger.debug('Starting key press thread for push button monitor')

        while not self._timeToExit:
            try:
                if self._listening:
                    self.pollPushButtons()
                self.onTick()  # event callback for animation
                sleep(self.DEBOUNCE_INTERVAL)

            except Exception, e:
                exType, ex, tb = sys.exc_info()
                logger.critical("Exception occurred of type %s in push button monitor" % (exType.__name__))
                logger.critical(str(e))
                traceback.print_tb(tb)


# ------------------------------------------------------------------------------
class VibrationMotor(IVibrationMotor):
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 name,
                 outputPin):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            name (string): Name of this motor, example "Huey"
            outputPin (string): Letter Designation of Pin , "E", "F", "G", or"H"
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        self.Name = name
        #TODO - Need to get these from config file [SS]
        #self.OnDuration_s = 0.5
        #self.OffDuration_s = 0.5
        self.outputPin = getattr(pibrella.output, outputPin)

    # --------------------------------------------------------------------------
    def __enter__(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Entering vibration motor %s', self.Name)
        return self

    # --------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Exiting vibration motor %s', self.Name)
        self.stop()

    # --------------------------------------------------------------------------
    def start(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Started vibration motor \"%s\".', self.Name)
        self.outputPin.on()

    # --------------------------------------------------------------------------
    def stop(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Stopped vibration motor \"%s\".', self.Name)
        self.outputPin.off()

# ------------------------------------------------------------------------------
class UrgencyLed(IUrgencyLed):
    # --------------------------------------------------------------------------
    def __init__(self,
                 name,
                 outputPin):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            name (string): Name of this motor, example "Huey"
            outputPin (string): Letter Designation of Pin , "E", "F", "G", or"H"
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        self.Name = name
        logger.debug('Constructing urgency LED %s' % (self.Name))

        #TODO - Need to get these from config file [SS]
        self.min_period_ms = 300
        self.max_period_ms = 2000

        self.outputPin = getattr(pibrella.output, outputPin)

        self._timeToExit = False
        self._transitionToStarted = False

        self._thread = Thread(target = self.run)
        self._thread.daemon = True
        self._thread.start()
    
    # --------------------------------------------------------------------------
    def __enter__(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Entering urgency LED %s', self.Name)
        return self
		
    # --------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Exiting urgency LED %s', self.Name)
        self.stop()		
        stopListening(self)
        self._timeToExit = True
        self._thread.join()
		
    # --------------------------------------------------------------------------
    def computeDelay(self,
                     percentComplete):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """

        delay_ms = (1.0 - percentComplete) * self.max_period_ms + percentComplete * self.min_period_ms

        logger.debug('computeDelay({}) returning {}'.format(percentComplete, delay_ms))
        return delay_ms

    # --------------------------------------------------------------------------
    def run(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.info('Starting thread for urgency LED %s' % (self.Name))

        delay_s = self.max_period_ms / 1000.0

        while not self._timeToExit:
            try:
                if self._transitionToStarted:
                    if self.flag:
                        self.flag = False
                        self.outputPin.off()
                        logger.debug('urgency LED \"%s\" pin off.', self.Name)
                    else:
                        self.flag = True
                        self.outputPin.on()
                        logger.debug('urgency LED \"%s\" pin on.', self.Name)

                    now = datetime.datetime.now()
                    currentDelta = now - self.startTime
                    current_ms = int(currentDelta.total_seconds() * 1000.0)
                    delay_ms = self.computeDelay(current_ms * 1.0 / self.boom_ms)
                    delay_s = delay_ms / 1000.0
                    logger.debug('current_ms={} vs. boom_ms={} => quotient={}, delay_ms={}, delay_s={}'.format(current_ms, self.boom_ms, current_ms * 1.0 / self.boom_ms, delay_ms, delay_s))

                    if current_ms >= self.boom_ms:
                        logger.info('Urgency LED %s transitioning to stopped.' % (self.Name))
                        self._transitionToStarted = False

                        delay_s = self.max_period_ms / 1000.0

                    logger.debug('Urgency LED thread sleeping for {} s.'.format(delay_s))
                else:
                    pass # Nothing to do

                sleep(delay_s)
            except Exception, e:
               exType, ex, tb = sys.exc_info()
               logger.critical("Exception occurred of type %s in urgency LED %s: %s" % (exType.__name__, self.Name, str(e)))
               traceback.print_tb(tb)

        logger.info('Stopping thread for urgency LED %s' % (self.Name))


    # --------------------------------------------------------------------------
    def start(self,
              total_epoch_ms):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        
        self.flag = True
        self.outputPin.on()
        self.startTime = datetime.datetime.now()
        self.boomTime = self.startTime + datetime.timedelta(milliseconds=total_epoch_ms)
        self.boomDelta = self.boomTime - self.startTime
        self.boom_ms = int(self.boomDelta.total_seconds() * 1000.0)

        logger.info('Urgency LED {} transitioning to started at time {} for boom at {} with total_epoch_ms={}.'.format(self.Name, self.startTime, self.boomTime, total_epoch_ms))
        self._transitionToStarted = True

    # --------------------------------------------------------------------------
    def stop(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Stopped urgency LED \"%s\".', self.Name)
        self.outputPin.off()
        self._transitionToStarted = False

# ------------------------------------------------------------------------------
class Buzzer(IBuzzer):
    """
    The buzzer class enables a pibrella buzzer to be play or stop a
    single note, or play a preconfigured song asynchronously.
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 name, 
                 config):
        """Initializes the Buzzer class

        TODO Detailed multi-line description if
        necessary.

        Args:
            name (string): Name of this instance of the Buzzer class. Example "Bob"
            config (Config): Conifg object containing an array named Song which is an
                             array of configuration objects with Tone and Duration.
                             Where Tone is an int from 0-TBD and Duration is a number
                             with the duration of time in seconds. 
        Returns:
            N/A
        Raises:
            N/A

        """
        self.Name = name
        # Copy the song to play
        self._song = []
        self.TotalDuration = 0
        for i in config.Song:
           # TODO verify there is not just a copy constructor for config
           # TODO verify tone is an int and Duration is a number
           tmp = Config()

           isFile = False
           hasTrack = False
           # Depending on how used these might not be there
           if hasattr(i, 'File') and i.File != None:
               tmp.File = i.File
               isFile = True
           if hasattr(i, 'Track') and i.Track != None:
               tmp.Track = i.Track
               hasTrack = True
           if hasattr(i, 'Tone') and i.Tone != None:
               tmp.Tone = i.Tone
           if hasattr(i, 'Duration') and i.Duration != None:
               tmp.Duration = i.Duration
           self._song.append(tmp)

           if isFile and hasTrack:
              if os.path.isfile(i.File):
                 # this is likely a midi now things get hard
                 try:
                    logger.debug('Opening midi file \"%s\".' % (i.File))
                    mid = MidiFile(i.File)
                    logger.debug('Opened midi file \"%s\".' % (i.File))
                    # now find the track
                    for track in enumerate(mid.tracks):
                       if hasattr(track, 'name') and track.name == i.Track:
                          for message in track:
                             if message.type == 'note_on':
                                # need to force data type to avoid int division
                                duration = 0.0 + message.time
                             elif message.type == 'note_off':
                                duration = message.time - duration
                                if duration > 0:  
                                   self.TotalDuration += duration/1000.0
                 except Exception, e:
                    exType, ex, tb = sys.exc_info()
                    logger.critical("Exception occurred of type %s in Buzzer run" % (exType.__name__))
                    logger.critical(str(e))
                    traceback.print_tb(tb)
              else:
                 # The file does not exist
                 logger.critical("The buzzer %s file %s does not exist", self.Name, i.File)
           else:
              # duration is easy just add em up
              self.TotalDuration += i.Duration
        self._setBuzzer()
        self._stopPlaying = False
        self._isWaitingForPlay = True
        self._isCutShort = False
        self._thread = Thread(target=self.run)
        self._thread.start()

    # --------------------------------------------------------------------------
    def _setBuzzer(self):   
        self._buzzer = getattr(pibrella, 'buzzer')

    # --------------------------------------------------------------------------
    def __enter__(self):
        logger.debug('Entering Buzzer')
        return self

    # --------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Exiting Buzzer')
        # This did not appear to be getting called so moved to stop

    # --------------------------------------------------------------------------
    def stop(self):
        self.off()
        self._isWaitingForPlay = True
        self._stopPlaying = True
        logger.debug('Before Join in Buzzer stop')
        self._thread.join()
        logger.debug('After Join in Buzzer stop')

    # --------------------------------------------------------------------------
    def play(self):
        """Asynchronously plays this Buzzer's song.

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Buzzer starting to play configured song')
        if (not self._stopPlaying) and (not self._isWaitingForPlay):
           # The song is already playing so need to restart it
           self.off()
        self._isWaitingForPlay = False

    # --------------------------------------------------------------------------
    def playSynchronously(self):
        """Synchronously plays this Buzzer's song.

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Buzzer starting to play configured song')
        if (not self._stopPlaying) and (not self._isWaitingForPlay):
           # The song is already playing so need to restart it
           self.off()
        self._isWaitingForPlay = True
        self._playOnce()

    # --------------------------------------------------------------------------
    def note(self,
             tone):
        """Has the buzzer hold a note unit off is called.

        So pibrella docs are light but looking at it's source code would suggest
        that the tone field is the standard midi value minus 69 so negative is
        allowed and 0-11 would be with higher or lower values just in different
        octaves:
        note_key = ['A','A#','B','C','C#','D','D#','E','F','F#','G','G#']
        As -49 would be below midi A0 this value is used to denote a rest.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Buzzer playing note %s' % tone)
        # TODO verify tone is an int
        if (not self._stopPlaying) and (not self._isWaitingForPlay):
            # The song is already playing so need to stop it
            self.off()
        if not (tone == '-'):
            self._buzzer.note(tone)

    # --------------------------------------------------------------------------
    def off(self):
        """Stops playing the buzzer's song or note.

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Stop playing Buzzer')
        if (not self._stopPlaying) and (not self._isWaitingForPlay):
            self._isCutShort = True
            while self._isCutShort:
                sleep(0.0001)
        self._buzzer.off()

    # --------------------------------------------------------------------------
    def _playOnce(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """

        for i in self._song:
           # first assess if this is a string of notes or a midi file
           if hasattr(i,'File'):
              # this is likely a midi
              try:
                 mid = MidiFile(i.File)
                 # now find the track to play
                 for track in mid.tracks:
                    if hasattr(track, 'name') and track.name == i.Track:
                       for message in track:
                          # if asynch give a way to stop
                          if self._stopPlaying or self._isCutShort:
                             self._buzzer.off()
                             self._isCutShort = False #reset for next run
                             break
                          if message.type == 'note_on':
                             note = message.note - 69
                             self._buzzer.note(note)
                             # need to force data type to avoid int division
                             duration = 0.0 + message.time
                          elif message.type == 'note_off':
                             duration = message.time - duration
                             if duration > 0:
                                sleep(duration/1000.0)
                             self._buzzer.off()
                 self._buzzer.off()
              except Exception, e:
                 exType, ex, tb = sys.exc_info()
                 logger.critical("Exception occurred of type %s in Buzzer run" % (exType.__name__))
                 logger.critical(str(e))
                 traceback.print_tb(tb)
           else:
              try:  
                 # if asynch give a way to stop
                 if self._stopPlaying or self._isCutShort:
                    self._buzzer.off()
                    isCutShort = False #reset for next run
                    break
                 if i.Tone == -49: 
                     self._buzzer.off()
                 else:
                     self._buzzer.note(i.Tone)
                 sleep(i.Duration)
                 self._buzzer.off()
              except Exception, e:
                 exType, ex, tb = sys.exc_info()
                 logger.critical("Exception occurred of type %s in Buzzer run" % (exType.__name__))
                 logger.critical(str(e))
                 traceback.print_tb(tb)
        # End for i

        self._isWaitingForPlay = True

    # --------------------------------------------------------------------------
    def run(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """

        # Note doing it this way gets rid of issue of restarting a thread
        # if you need to stop short, but it chews up CPU
        # TODO there needs to be a better way of using a worker thread instead
        # of a self thread but still be able to signal the worker thread to stop
        # early without relying on a member variable.
        while not self._stopPlaying:
           if self._isWaitingForPlay:
               sleep(0.001)
           else:
               self._playOnce()
        logger.debug('Run over for Buzzer')

# ------------------------------------------------------------------------------
class FakeHwBuzzer():
    """
    The FakeHwBuzzer class enables a pibrella buzzer interface to be simulated,
    without making any noise but displaying debug info.
    """

    # --------------------------------------------------------------------------
    def off(self):
       pass

    # --------------------------------------------------------------------------
    def note(self, tone):
       pass

# Inheriting from Buzzer to attempt to keep this timing as close as HW as possible.
# ------------------------------------------------------------------------------
class SilentBuzzer(Buzzer):
    """
    The buzzer class enables a fake console buzzer to be play or stop a
    single note, or play a preconfigured song asynchronously.
    """
    # --------------------------------------------------------------------------
    def _setBuzzer(self):   
        self._buzzer = FakeHwBuzzer()

# ------------------------------------------------------------------------------
class Input(IInput):
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 name,
                 inputPin):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            name (string): Name of this input, example "lightDetector"
            inputPin (string): Letter Designation of Pin , "a", "b", "c", or"d"
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        self.Name = name
        self._inputPin = getattr(pibrella.input, inputPin)

    # --------------------------------------------------------------------------
    def read(self):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        return self._inputPin.read()

# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

