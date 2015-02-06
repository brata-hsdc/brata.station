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
    START_STATE            =  0
    IDLE_STATE             =  1
    PRE_INPUT_STATE        =  2
    INPUT_STATE            =  3
    SUBMITTING_STATE       =  4
    SUBMITTED_STATE        =  5
    PASSED_STATE           =  6
    FAILED_STATE           =  7
    SHUTDOWN_STATE         =  8
    PRE_IDLE_STATE         =  9
    PRE_PASSED_STATE       = 10
    PRE_FAILED_STATE       = 11
    PRE_FAILED_RETRY_STATE = 12
    FAILED_RETRY_STATE     = 13
    SEND_RESULT_STATE      = 14
    SEND_FINISH_STATE      = 15
    ERROR_STATE            = 99
    
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
            config:    a Config object containing properties to configure station characteristics
            hwModule:  python module object that defines hardware interfaces
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
        self.ConnectionManager = None
        
        self._combo = None  # will hold a Combo object
        self._timedMsg = None  # generator
        self._timedMsgNextState = self.IDLE_STATE
        self._colorToggle = None  # generator
        
        self._preInputDuration   =  6.0  # seconds to display msg
        self._passedDuration     =  7.5  # seconds to display msg
        self._failedDuration     =  5.0  # seconds to display msg
        self._preIdleDuration    =  5.0  # seconds to display msg
        self._prePassedDuration  =  5.0  # seconds to display msg
        self._preFailedDuration  =  5.0  # seconds to display msg
        self._submittedDuration  =  2.0  # seconds to display msg
        self._sendFinishDuration = 15.0  # seconds to display msg
        
        
        # Background cycle states: ([list of colors], rate_in_sec)
        # TODO: These constants could be moved to runstation.conf
        self._preIdleBg    = (["CYAN"], 1.0)
        self._prePassedBg  = (["YELLOW", "WHITE"], 0.1)
        self._preFailedBg  = (["YELLOW", "WHITE"], 0.1)
        self._idleBg       = (["WHITE", "BLUE", "YELLOW", "GREEN", "RED", "CYAN", "MAGENTA"], 0.75)
        self._preInputBg   = (["YELLOW", "YELLOW", "YELLOW", "YELLOW", "RED"], 0.15)
        self._inputBg      = (["CYAN"], 1.0)
        self._submit1Bg    = (["RED", "WHITE"], 0.15)
        self._submit2Bg    = (["WHITE"], 1.0)
        self._passedBg     = (["GREEN", "CYAN"], 1.0)
        #self._failedBg    = (["RED"], 1.0)
        self._failedBg     = (["RED", "RED", "RED", "RED", "RED", "RED", "RED", "RED", "RED", "WHITE"], 0.1)
        self._sendFinishBg = (["YELLOW", "YELLOW", "YELLOW", "YELLOW", "RED"], 0.15)
        self._shutdownBg   = (["BLUE"], 1.0)
        self._errorBg      = (["RED", "RED", "RED", "RED", "RED", "WHITE"], 0.15)
        
        # Display text for different states
        # TODO: These constants could be moved to runstation.conf
        self._preIdleText         = "  Resetting...\n"
        self._prePassedText       = "- Trying Your -\n- Combination -"
        self._preFailedText       = "- Trying Your -\n- Combination -"
        self._idleText            = "==== CRACK =====\n== THE = SAFE =="
        self._preInputText        = "      HEY!!\n  Scan QR Code"
        self._enterLine1Text      = "Enter Code:"
        self._submittingLine1Text = "2nd ENTER Sends"
        self._submittedLine1Text  = "=Code Submitted="
        self._passedText          = "  The Safe Is\n    UNLOCKED"
        self._failedText          = "  The Safe Is\n  STILL LOCKED"
        self._sendFinishText      = "     Submit\n   Your  Data"
        self._shutdownText        = "Shutting down..."
        self._errorText           = "  Malfunction!\n"

        # Station current operating state
        self._ctsState = self.START_STATE
        self._pushButtonMonitor.setOnTickCallback(self.onTick)
        self.enterState(self.IDLE_STATE)

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
        self.enterState(self.SHUTDOWN_STATE)

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
        self.enterState(self.IDLE_STATE)

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
        self.refreshDisplayedCombo()
        self.enterState(self.INPUT_STATE)

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
    def enterState(self, newState):
        """ Transition to the specified operating state
        
        This will modify the display text, the display background, the state of
        running timers, and the state of the _pushButtonMonitor.
        
        Returns:
            The state prior to being called
        """
        oldState = self._ctsState
        
#         if newState != self._ctsState:
        while newState != self._ctsState:
            
            if self._ctsState in (self.PRE_INPUT_STATE,
                                  self.PRE_IDLE_STATE,
                                  self.PRE_PASSED_STATE,
                                  self.PRE_FAILED_STATE,
                                  self.PRE_FAILED_RETRY_STATE,
                                  self.FAILED_RETRY_STATE,
                                  self.PASSED_STATE,
                                  self.FAILED_STATE,
                                  self.SUBMITTED_STATE,
                                  self.SEND_FINISH_STATE,
                                  ):  # leaving this state
                self._timedMsg = None
            
            if newState == self.PRE_IDLE_STATE:
                self._timedMsg = self.displayTimedMsg(self._preIdleText, self._preIdleDuration, self._preIdleBg, self.IDLE_STATE)

            elif newState == self.IDLE_STATE:
                self._display.setText(self._idleText)
                self.setToggleColors(*self._idleBg)
                self._pushButtonMonitor.startListening()
                
            elif newState == self.PRE_INPUT_STATE:
                self._timedMsg = self.displayTimedMsg(self._preInputText, self._preInputDuration, self._preInputBg, self.IDLE_STATE)
                self._pushButtonMonitor.stopListening()
                
            elif newState == self.INPUT_STATE:
                self._display.setLine1Text(self._enterLine1Text)
                self.setToggleColors(*self._inputBg)
                self.refreshDisplayedCombo()
                self._pushButtonMonitor.startListening()
                
            elif newState == self.SUBMITTING_STATE:
                self._display.setLine1Text(self._submittingLine1Text)
                self.setToggleColors(*self._submit1Bg)
                
            elif newState == self.SUBMITTED_STATE:
#                 self._display.setLine1Text(self._submittedLine1Text)
#                 self.setToggleColors(*self._submit2Bg)
                logger.debug("initializing SUBMITTED_STATE")
                self._timedMsg = self.displayTimedMsg(self._submittedLine1Text, self._submittedDuration, self._submit2Bg, self.SEND_RESULT_STATE)
                self._pushButtonMonitor.stopListening()
                
            elif newState == self.SEND_RESULT_STATE:
                # Submit combo to MS
                self.submitCombination()
                
            elif newState == self.PRE_PASSED_STATE:
                self._timedMsg = self.displayTimedMsg(self._prePassedText, self._prePassedDuration, self._prePassedBg, self.PASSED_STATE)

            elif newState == self.PASSED_STATE:
                self._timedMsg = self.displayTimedMsg(self._passedText, self._passedDuration, self._passedBg, self.SEND_FINISH_STATE)
                
            elif newState == self.PRE_FAILED_RETRY_STATE:
                self._timedMsg = self.displayTimedMsg(self._preFailedText, self._preFailedDuration, self._preFailedBg, self.FAILED_RETRY_STATE)
                
            elif newState == self.FAILED_RETRY_STATE:
                self._timedMsg = self.displayTimedMsg(self._failedText, self._failedDuration, self._failedBg, self.INPUT_STATE)
                
            elif newState == self.PRE_FAILED_STATE:
                self._timedMsg = self.displayTimedMsg(self._preFailedText, self._preFailedDuration, self._preFailedBg, self.FAILED_STATE)
                
            elif newState == self.FAILED_STATE:
                self._timedMsg = self.displayTimedMsg(self._failedText, self._failedDuration, self._failedBg, self.SEND_FINISH_STATE)
                
            elif newState == self.SEND_FINISH_STATE:
                self._timedMsg = self.displayTimedMsg(self._sendFinishText, self._sendFinishDuration, self._sendFinishBg, self.PRE_IDLE_STATE)
                
            elif newState == self.SHUTDOWN_STATE:
                self._display.setText(self._shutdownText)
                self.setToggleColors(*self._shutdownBg)
                self._pushButtonMonitor.stopListening()

            else:
                self._display.setText(self._errorText)
                self.setToggleColors(*self._errorBg)
                self._pushButtonMonitor.stopListening()
            
            self._ctsState = newState
        
        return oldState
        
    # --------------------------------------------------------------------------
    def buttonPressed(self,
                      pushButtonName):
        """ Handle combination input pushbutton events.

        Only recognizes the push event, not the release.  Buttons update the
        displayed combo, and may change the operating state.

        Args:
            pushButtonName (string): Up, Down, Left, Right, or Enter
        """
        #logger.info('Push button %s pressed.' % (pushButtonName))
        if self._ctsState == self.IDLE_STATE:
            self.enterState(self.PRE_INPUT_STATE)
        elif pushButtonName == 'Up':
            if self.enterState(self.INPUT_STATE) == self.INPUT_STATE:
                self._combo.incCurrentDigit(1)
                self.refreshDisplayedCombo()
        elif pushButtonName == 'Down':
            if self.enterState(self.INPUT_STATE) == self.INPUT_STATE:
                self._combo.decCurrentDigit(1)
                self.refreshDisplayedCombo()
        elif pushButtonName == 'Left':
            if self.enterState(self.INPUT_STATE) == self.INPUT_STATE:
                self._combo.moveLeft(1)
                self.refreshDisplayedCombo()
        elif pushButtonName == 'Right':
            if self.enterState(self.INPUT_STATE) == self.INPUT_STATE:
                self._combo.moveRight(1)
                self.refreshDisplayedCombo()
        elif pushButtonName == 'Enter':
            if self._ctsState == self.INPUT_STATE:
                self.enterState(self.SUBMITTING_STATE)
                logger.info('1st enter key press received. Waiting for 2nd.')
            elif self._ctsState == self.SUBMITTING_STATE:
                self.enterState(self.SUBMITTED_STATE)
                logger.info('2nd enter key press received.')
                
                #self._ctsState = self.SUBMITTED_STATE
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
        theatric_delay, is_correct, challenge_complete = args
        if challenge_complete.lower() == "true":
            self.enterState(self.PRE_FAILED_STATE)
        else:
            self.enterState(self.PRE_FAILED_RETRY_STATE)

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
        self.enterState(self.PRE_PASSED_STATE)

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
        self.enterState(self.ERROR_STATE)

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
    def displayTimedMsg(self, msg, duration, bg, nextState):
        """ Display msg for duration, then go back to IDLE_STATE
        
        This is a generator function.  When first called, it sets the display
        text and background, and returns a generator object.
        Each time the generator's next() method is called it evaluates the current
        time.  Once a sufficient time interval has passed, it returns False.  Before
        that time it returns True.
        
        Sample usage:
            timedMsg = self.DisplayTimedMsg("I'm here for a second", 1.0, (["RED", "GREEN", "BLUE"], 0.2))
            while timedMsg.next():
                sleep(0.1)
            timedMsg = None
        
        Args:
            msg (string):  A message to be displayed
            duration (float):  Seconds to display msg
            bg (list, float):  Args to pass to self.toggleColors
            nextState (STATE):  The state to enter after time expires
        
        Returns:
            a generator function that returns False when finished
        """
        tStart = time.time()
        if "\n" in msg:
            self._display.setText(msg)
        else:
            self._display.setLine1Text(msg)
        self.setToggleColors(*bg)
        self._timedMsgNextState = nextState
        
        while time.time() - tStart < duration:
            yield True  # keep displaying the msg
        yield False     # finished

    # --------------------------------------------------------------------------
    def toggleColors(self, colors, interval):
        """ Toggle background colors every interval seconds.
        
        This is a generator function.  When called, it returns a generator object.
        Each time the generator's next() method is called it evaluates the current
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
        Returns:
            a generator function that cycles through a list of background colors
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
            and time message display
        """
        if self._colorToggle:
            self._colorToggle.next()
        
        if self._timedMsg:
            if not self._timedMsg.next():
                self._timedMsg = None
                self.enterState(self._timedMsgNextState)
        
    # --------------------------------------------------------------------------
    def submitCombination(self):
        """ Send the combination to the Master Server.
        
        This method is called when the user presses the SELECT (Enter) button
        twice in succession.  The current value of the combination in the
        display (self._combo.toList()) is transmitted to the Master Server.
        """
        combo = self._combo.toList()  # get combination as a list of three integers
        isCorrect = self._combo.isMatch()
        
        logger.info('Submitting combo: {} , match = {}'.format(repr(combo), isCorrect))
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
        return reduce(operator.and_, map(operator.eq, self._digits, self._targetDigits))

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

