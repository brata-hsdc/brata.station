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

import logging
import logging.handlers
# TODO Is UnresolvedImport needed? hw.py should not be enabled on a non-Pi; same for LCD below.
import pibrella  # @UnresolvedImport when not on R-Pi
import signal
import sys
from time import sleep
from threading import Thread
import traceback
from threading import Thread
from time import sleep
import operator

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
from station.util import Config
# TODO NonBlockingConsole was meant to be used with station.console to get keyboard input; it should not be needed in hw.py
from station.util import NonBlockingConsole
from station.console import PushButton # TODO shouldn't have a console import in this file

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

class PibrellaLedFacade():
    def __init__(self, chan, val, step, enabled):
        self._val = val
        self._step = step
        self._chan = chan
        self.enabled = enabled
        self._gamma = []
        for i in range(4096):
            self._gamma.append(int(pow(i/4095.0, 2.8)*4095))
        initialValue = self._gamma[0]
        if self.enabled:
            initialValue = self._gamma[self._val]
        self._pwm = PWM(0x40, debug=True)
        self._pwm.setPWMFreq(400)
        self._pwm.setPWM(self._chan, 0, initialValue)

    def __exit__(self, type, value, traceback):
        pass

    def on(self):
        self._pwm.setPWM(self._chan, 0, self._gamma[self._val])

    def off(self):
        self._pwm.setPWM(self._chan, 0, self._gamma[0])

    def fade(self, startPercentageOn, endPercentageOn, durationInSeconds):
        # TODO ideally this should be implemented to match pibrella and remove decay
        pass

    def pulse(self, fadeInTime, fadeOutTime, onTime, offTime):
        # TODO
        pass

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
        logger.debug('Set LED steady ON \"%s\".', self.Name)
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
        logger.debug('Set LED steady OFF \"%s\".', self.Name)
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

    def decay(self):
         """ See interface definition
         """
         pass

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
        with NonBlockingConsole() as nbc:
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
        self._buzzer = getattr(pibrella, 'buzzer')
        self._stopPlaying = False
        self._isWaitingForPlay = True
        self._isCutShort = False
        self._thread = Thread(target=self.run)
        self._thread.start()

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
        self._isWaitingForPlay = True
        self._stopPlaying = True
        self._thread.join()

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
                             pibrella.buzzer.note(note)
                             # need to force data type to avoid int division
                             duration = 0.0 + message.time
                          elif message.type == 'note_off':
                             duration = message.time - duration
                             if duration > 0:
                                sleep(duration/1000.0)
                             pibrella.buzzer.off()
                 pibrella.buzzer.off()
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
               sleep(0.0001)
           else:
               self._playOnce()

# TODO use inheritance to deduplicate this class and the console.Buzzer class.
# ------------------------------------------------------------------------------
class SilentBuzzer(IBuzzer):
    """
    The buzzer class enables a fake console buzzer to be play or stop a
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
        logger.debug('Init buzzer \"%s\".' % self.Name)
        # Copy the song to play
        self._song = []
        self.TotalDuration = 0
        for i in config.Song:
           # TODO verify there is not just a copy constructor for config
           # TODO verify tone is an int and Duration is a number
           tmp = Config()

           # Depending on how used these might not be there
           if hasattr(i, 'File') and i.File != None:
               tmp.File = i.File 
           if hasattr(i, 'Track') and i.Track != None:
               tmp.Track = i.Track
           if hasattr(i, 'Tone') and i.Tone != None:
               tmp.Tone = i.Tone
           if hasattr(i, 'Duration') and i.Duration != None:
               tmp.Duration = i.Duration
           self._song.append(tmp)

           if hasattr(i, 'File') and i.File != None:
              if os.path.isfile(i.File):
                 # this is likely a midi now things get hard
                 try:
                    logger.debug('Opening midi file \"%s\".' % i.File)
                    mid = MidiFile(i.File)
                    logger.debug('Opened midi file \"%s\".' % i.File)
                    # now find the track
                    for track in mid.tracks:
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
        self._stopPlaying = True
        self._thread = Thread(target=self.run)
        #self._thread.daemon = True
        # Only start the thread to play the song when commanded.

    # --------------------------------------------------------------------------
    def __enter__(self):
        logger.debug('Entering SilentBuzzer')
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
        logger.debug('Exiting SilentBuzzer')
        self._stopPlaying = True
        self._thread.join()

    # --------------------------------------------------------------------------
    def play(self):
        """Asynchronously plays this SilentBuzzer's song.

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
        logger.debug('SilentBuzzer starting to play configured song')
        if not self._stopPlaying:
           # The song is already playing so need to restart it
           self.off()
        self._stopPlaying = False
        self._thread.start()

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
        logger.debug('SilentBuzzer starting to play configured song')
        if not self._stopPlaying:
           # The song is already playing so need to restart it
           self.off()
        self._stopPlaying = False
        self.run()

    # --------------------------------------------------------------------------
    def note(self,
             tone):
        """Has the buzzer hold a note unit off is called.

        So pibrella docs are light but looking at it's source code would suggest
        that the tone field is the standard midi value minus 69 so negative is
        allowed and 0-11 would be with higher or lower values just in different
        octaves:
        note_key = ['A','A#','B','C','C#','D','D#','E','F','F#','G','G#']

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
        logger.debug('SilentBuzzer playing note %s' % tone)
        # TODO verify tone is an int

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
        logger.debug('Stop playing SilentBuzzer')
        if not self._stopPlaying:
           # Need to stop the song thread first
           self._stopPlaying = True
           # TODO fix SilentBuzzer threading self._thread.join()
        logger.debug('SilentBuzzer turning off')

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

        for i in self._song:
           # first assess if this is a string of notes or a midi file
           if hasattr(i,'File'):
              if os.path.isfile(i.File):
                 # this is likely a midi
                 try:
                    mid = MidiFile(i.File)
                    # now find the track
                    for track in enumerate(mid.tracks):
                       if hasattr(track, 'name') and track.name == i.Track:
                          for message in track:
                             if message.type == 'note_on':
                                note = message.note - 69
                                logger.debug('Buzzer playing note %s' % note)
                                # need to force data type to avoid int division
                                duration = 0.0 + message.time
                             elif message.type == 'note_off':
                                duration = message.time - duration
                                if duration > 0:
                                   sleep(duration/1000.0)
                                logger.debug('SilentBuzzer turning off')
                    logger.debug('Buzzer turning off')
                 except Exception, e:
                    exType, ex, tb = sys.exc_info()
                    logger.critical("Exception occurred of type %s in SilentBuzzer run" % (exType.__name__))
                    logger.critical(str(e))
                    traceback.print_tb(tb)
              else:
                 # The file does not exist
                 logger.critical("The SilentBuzzer %s file %s does not exist", self.Name, i.File)
           else:
              try:  
                 if self._stopPlaying:
                    logger.debug('SilentBuzzer turning off')
                    break
                 logger.debug('SilentBuzzer playing note %s' % i.Tone)
                 sleep(i.Duration)
              except Exception, e:
                 exType, ex, tb = sys.exc_info()
                 logger.critical("Exception occurred of type %s in SilentBuzzer run" % (exType.__name__))
                 logger.critical(str(e))
                 traceback.print_tb(tb)

        self._stopPlaying = True

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

