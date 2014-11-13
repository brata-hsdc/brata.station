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
import pibrella  # @UnresolvedImport when not on R-Pi
import signal
import sys
import traceback
from threading import Thread
from time import sleep
import operator

import Adafruit_CharLCD as LCD    # @UnresolvedImport when not on R-Pi
from interfaces import IDisplay
from interfaces import ILed
from interfaces import IPushButtonMonitor
from interfaces import IVibrationMotor
from station.util import NonBlockingConsole
from station.console import PushButton


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
        logger.debug('Display line width: {}'.format(self._lineWidth))
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
    def setBgColor(self, color):
        ''' Set the display background color to the specified color.
        
        Sets the display backlight to the color specified by the color name parameter.
        The valid color names are "BLACK", "RED", "GREEN", "BLUE", "CYAN", "YELLOW",
        "MAGENTA", "WHITE".

        Raises:
            KeyError if color is not one of the valid color string values.
        '''
        self._lcd.set_color(*self.COLORS[color])
    
    # --------------------------------------------------------------------------
    def lineWidth(self):
        """ Returns: the number of columns in a line of the display.
        """
        return self._lineWidth

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
        self._lcd.blink(show)
        self._lcd.show_cursor(show)
        
    # --------------------------------------------------------------------------
    def setCursor(self, row=0, col=0):
        """ Sets the position of the cursor and makes it visible.
        """
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
        self.outputPin = getattr(pibrella.light, config.OutputPin)

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
        self.outputPin.pulse(0, 0, self.FlashingOnDuration_s, self.FlashingOffDuration_s);


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
        # Sample the current state of all buttons
        buttonInputs = map(self._device.is_pressed, self.BUTTONS)
        
        # Convert prevState, input to an index = 2*state + input
        buttonStateTransitions = map(lambda s,i: 2*s+(1 if i else 0), self._buttonStates, buttonInputs)
            
        # Use the transition to lookup the next state
        self._buttonStates = [self.NEXT_STATE[i] for i in buttonStateTransitions]
        
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
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

