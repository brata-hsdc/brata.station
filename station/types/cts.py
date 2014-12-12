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
Provides the definitions needed for the CTS station type.
"""

import operator
import logging
import logging.handlers
import time

from station.interfaces import IStation


# ------------------------------------------------------------------------------
class Station(IStation):
    """
    Provides the implementation for a CTS station to support displaying and
    obtaining a combination value from the user to supply to the MS.
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 config,
                 hwModule):
        """ Initialize the LCD display and the pushbutton monitor

        The LCD 2-line display will display a status message on the first line
        and a 6-digit combination code on the second line.  The pushbuttons will
        allow the user to move the digit entry cursor LEFT or RIGHT, increase (UP)
        or decrease (DOWN) the value of the digit under the cursor, and submit
        the code by pressing the SELECT button twice.

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
        logger.debug('Constructing CTS')

        displayClassName = config.DisplayClassName
        pushButtonMonitorClassName = config.PushButtonMonitorClassName

        displayClass = getattr(hwModule, displayClassName)
        pushButtonMonitorClass = getattr(hwModule, pushButtonMonitorClassName)

        self._display = displayClass(config.Display)
        self._display.setText("Initializing...")

        logger.info('Initializing pushButtonMonitor')
        self._pushButtonMonitor = pushButtonMonitorClass()
        self._pushButtonMonitor.setDevice(self._display._lcd)

        for i in config.PushButtons:
            logger.info('  Setting button {}'.format(i))
            self._pushButtonMonitor.registerPushButton(i.Name,
                                                       self.buttonPressed,
                                                       i)

        self._centerOffset = 0  # amount of space to left of displayed combination
        self._submitting = False
        self.ConnectionManager = None
        
        self._combo = None  # will hold a Combo object
        self._colorToggle = None
        self._resetBg = (["YELLOW", "MAGENTA", "WHITE", "MAGENTA"], 1.0)
        self._idleBg = (["WHITE"], 1.0)
        self._enterBg = (["CYAN"], 1.0)
        self._submit1Bg = (["YELLOW"], 1.0)
        self._submit2Bg = (["RED", "WHITE"], 0.15)
        
        self.setToggleColors(*self._idleBg)
        self._pushButtonMonitor.setOnTickCallback(self.onTick)


    # --------------------------------------------------------------------------
    @property
    def stationTypeId(self):
        """Identifies this station's type as CTS.

        Args:
            N/A.
        Returns:
            N/A.
        Raises:
            N/A.

        """
        return "CTS"

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
        logger.info('Starting CTS.')

        # Nothing more to do.

    # --------------------------------------------------------------------------
    def stop(self, signal):
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
        logger.info('Received signal "%s". Stopping CTS.', signal)
        self._display.setText("Shutting down...")

        self._pushButtonMonitor.stopListening()

    # --------------------------------------------------------------------------
    def onReady(self):
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
        logger.info('CTS transitioned to Ready state.')
        self._display.setText("Ready.")

        self._pushButtonMonitor.stopListening()

    # --------------------------------------------------------------------------
    def onProcessing(self,
                     args):
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
        logger.info('CTS transitioned to Processing state with args [%s].' % (args))

        self._combo = Combo(*args)

        self._display.setLine1Text("Enter code:")
        self.refreshDisplayedCombo()
        self.setToggleColors(*self._enterBg)

        self._pushButtonMonitor.startListening()

    # --------------------------------------------------------------------------
    def refreshDisplayedCombo(self):
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
        s = self._combo.toString()
        self._centerOffset = (self._display.lineWidth() - len(s)) // 2  # amount of space before s
        s = "{0:>{width}}".format(s, width=len(s) + self._centerOffset)
        self._display.setLine2Text(s)
        self._display.setCursor(1, self._combo.formattedPosition() + self._centerOffset)

    # --------------------------------------------------------------------------
    def buttonPressed(self,
                      pushButtonName):
        """ Handle combination input pushbutton events.

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
        #logger.info('Push button %s pressed.' % (pushButtonName))

        if pushButtonName == 'Up':
            self.setToggleColors(*self._enterBg)
            self._display.setLine1Text("Enter code:")
            self._combo.incCurrentDigit(1)
            self.refreshDisplayedCombo()
            self._submitting = False
        elif pushButtonName == 'Down':
            self.setToggleColors(*self._enterBg)
            self._display.setLine1Text("Enter code:")
            self._combo.decCurrentDigit(1)
            self.refreshDisplayedCombo()
            self._submitting = False
        elif pushButtonName == 'Left':
            self.setToggleColors(*self._enterBg)
            self._display.setLine1Text("Enter code:")
            self._combo.moveLeft(1)
            self.refreshDisplayedCombo()
            self._submitting = False
        elif pushButtonName == 'Right':
            self.setToggleColors(*self._enterBg)
            self._display.setLine1Text("Enter code:")
            self._combo.moveRight(1)
            self.refreshDisplayedCombo()
            self._submitting = False
        elif pushButtonName == 'Enter':
            if self._submitting:
                logger.info('2nd enter key press received.')
                # Submit combo to MS
                self.submitCombination()
                
                self._submitting = False
                self.setToggleColors(*self._submit1Bg)
                self._display.setLine1Text("=Code Submitted=")
                self._pushButtonMonitor.stopListening()
            else:
                logger.info('1st enter key press received. Waiting for 2nd.')
                self._submitting = True
                self.setToggleColors(*self._submit2Bg)
                self._display.setLine1Text("2nd ENTER Sends")
        else:
            logger.debug("Invalid pushButtonName received: '{}'".format(pushButtonName))

    # --------------------------------------------------------------------------
    def onFailed(self,
                 args):
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
        logger.info('CTS transitioned to Failed state with args [%s].' % (args))
        self._display.setText("Failed.")

        self._pushButtonMonitor.stopListening()

    # --------------------------------------------------------------------------
    def onPassed(self,
                 args):
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
        logger.info('CTS transitioned to Passed state with args [%s].' % (args))
        self._display.setText("Success!")

        self._pushButtonMonitor.stopListening()

    # --------------------------------------------------------------------------
    def onUnexpectedState(self, value):
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
        logger.critical('CTS transitioned to Unexpected state %s', value)
        self._display.setText("Malfunction!")

        self._pushButtonMonitor.stopListening()

    # --------------------------------------------------------------------------
    def setToggleColors(self, colors, interval=0.25):
        """ Set a sequence of background colors to flip through at the specified interval
        
        If a single color is passed in, the background is set, and the _colorToggle
        generator is deactivated.  If a list of colors is passed in, they are
        cycled at the specified interval until the generator's close() method is
        called.  If the colors list is empty, it defaults to ["WHITE"].
        
        Args:
            colors    (list):  A sequence of color names or a single color name
            interval (float):  The time interval in seconds between color switches
        """
        if self._colorToggle:
            self._colorToggle.close()  # stop the current generator
            
        # Make sure we have a list
        if isinstance(colors, (str, unicode)):
            colors = [colors]
            
        if len(colors) < 1:
            colors = ["WHITE"]
        if len(colors) > 1:
            self._colorToggle = self.toggleColors(colors, interval)
        else:
            # turn off toggle and display the single color
            self._colorToggle = None
            self._display.setBgColor(colors[0])
        
    # --------------------------------------------------------------------------
    def toggleColors(self, colors, interval):
        """ Toggle background colors every interval seconds.
        
        This is a generator function.  When called, it returns a generator object.
        Each time the generators next() method is called it evaluates the current
        time.  If a sufficient time interval has passed, it cycles to the
        next color in the colors list, and sets the LCD background color to the new
        color.  It returns the new color.
        
        Sample usage:
            colorCycle = self.toggleColors(["RED", "GREEN", "BLUE"], interval=1.0)
            while cycleColors:
                colorCycle.next()  # switch colors at approx. 1 Hz
                sleep(0.1)
        
        Args:
            colors    (list):  A list of valid color name strings
            interval (float):  Seconds between switching colors
        """
        tStart = 0.0  # make it toggle immediately
        
        while True:
            tNow = time.time()
            if tNow - tStart >= interval: # time to switch colors
                tStart = tNow                                  # save the new start time
                colors[:-1],colors[-1] = colors[1:],colors[0]  # rotate the list
                self._display.setBgColor(colors[-1])           # set the display
            yield colors[-1]

    # --------------------------------------------------------------------------
    def onTick(self):
        """ onTick callback to be attached to polling loop to animate bg color
        """
        if self._colorToggle:
            self._colorToggle.next()
        
    # --------------------------------------------------------------------------
    def submitCombination(self):
        """ Send the combination to the Master Server.
        
        This method is called when the user presses the SELECT (Enter) button
        twice in succession.  The current value of the combination in the
        display (self._combo.toList()) is transmitted to the Master Server.
        """
        combo = self._combo.toList()  # get combination as a list of three integers
        logger.info('Submitting combo: {}'.format(repr(combo)))

        # TODO: Issue 33 - compare submitted combo against self._combo
        isCorrect = True

        self.ConnectionManager.submitCtsComboToMS(combo, isCorrect)
    

# ------------------------------------------------------------------------------
class Combo:
    """
    Manages the state of the combination being entered.
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 value1,
                 value2,
                 value3):
        """ Initialize combination to 6 digits, 2 in value1, 2 in value2, and 2 in value3

        TODO Detailed multi-line description if
        necessary.

        Args:
            value1: int 00-99
            value2: int 00-99
            value3: int 00-99
        """
        logger.debug('Constructing combo')

        # TODO
        self._wrap = True  # wrap the cursor around
        self._position = 0
        self._digits = [0, 0, 0, 0, 0, 0]  # current state of entered combo
        self._sep = " "  # field separator character
        
        self._targetDigits = [0, 0, 0, 0, 0, 0]
        self._targetDigits[0] = value1 / 10 % 10
        self._targetDigits[1] = value1 /  1 % 10
        self._targetDigits[2] = value2 / 10 % 10
        self._targetDigits[3] = value2 /  1 % 10
        self._targetDigits[4] = value3 / 10 % 10
        self._targetDigits[5] = value3 /  1 % 10

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
        logger.debug('Entering combo %s', self.Name)
        # TODO
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
        logger.debug('Exiting combo')
        # TODO

    # --------------------------------------------------------------------------
    def isMatch(self):
        """ Returns:  True if _digits == _targetDigits.
        """
        return reduce(operator.and_, map(operator.eq, self._combination, self._target))

    # --------------------------------------------------------------------------
    def position(self):
        """ Returns:  The current cursor digit position.
        """
        return self._position

    # --------------------------------------------------------------------------
    def formattedPosition(self):
        """ Returns:  The cursor position in the formatted combination string.
        """
        return self._position + self._position//2  # one extra char for every 2 digits

    # --------------------------------------------------------------------------
    def moveLeft(self,
                 numPlaces=1):
        """ Move the digit cursor numplaces to the left.

        Move the digit cursor position numplaces to the left.  If _wrap is True,
        moving the cursor to the left of the first cursor position (0) will
        place the cursor at the last cursor position.  If _wrap is False,
        attempting to move the cursor to the left of the first cursor position
        will have no effect.

        Args:
            numPlaces (int): number of digit positions to move (default 1)
        """
        self._position -= numPlaces
        if self._wrap:
            self._position %= len(self._digits)
        else: # clamp
            self._position = max(self._position, 0)
        #logger.debug('moved current combo pos to %s' % (self._position))

    # --------------------------------------------------------------------------
    def moveRight(self,
                  numPlaces=1):
        """ Move the digit cursor numplaces to the right.

        Move the digit cursor position numplaces to the right.  If _wrap is True,
        moving the cursor to the right of the last cursor position (0) will
        place the cursor at the first cursor position.  If _wrap is False,
        attempting to move the cursor to the right of the last cursor position
        will have no effect.

        Args:
            numPlaces (int): number of digit positions to move (default 1)
        """
        self._position += numPlaces
        if self._wrap:
            self._position %= len(self._digits)
        else:
            self._position = min(self._position, len(self._digits)-1)
        #logger.debug('moved current combo pos to %s' % (self._position))

    # --------------------------------------------------------------------------
    def incCurrentDigit(self,
                        incrementValue=1):
        """ Increase the current digit by incrementValue.

        Increases the current digit value by incrementValue.  If the current
        value + incrementValue is greater than 10, higher digits are discarded.

        Args:
            incrementValue (int): the increase amount (default 1)
        Raises:
            IndexError: if self._position is out of range
        """
        self._digits[self._position] = (self._digits[self._position] + incrementValue) % 10

    # --------------------------------------------------------------------------
    def decCurrentDigit(self,
                        decrementValue=1):
        """ Decrease the current digit by decrementValue.

        Decreases the current digit value by decrementValue.  If the current
        value - decrementValue is less than 0, the digit wraps around.

        Args:
            decrementValue (int): the decrease amount (default 1)
        Raises:
            IndexError: if self._position is out of range
        """
        self.incCurrentDigit(-decrementValue)

    # --------------------------------------------------------------------------
    def toList(self):
        """ Convert the _digits list to a list of 3 ints

        Returns:
            List of 3 ints, each in the range 0-99
        """
        result = [self._digits[0] * 10 + self._digits[1],
                  self._digits[2] * 10 + self._digits[3],
                  self._digits[4] * 10 + self._digits[5]]
        return result

    # --------------------------------------------------------------------------
    def toString(self):
        """ Convert list of digits to formatted combination string.
        Returns:
            A string formatted as "nn:nn:nn" where ":" is the _sep character
        """
        s = "{}{}:{}{}:{}{}".format(*self._digits[0:6])
        s = s.replace(":", self._sep)
        #logger.debug('combo value for ({}{}, {}{}, {}{})'.format(*self._digits[0:6]))
        #logger.debug('      as string: "{}"'.format(s))

        return s

# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

