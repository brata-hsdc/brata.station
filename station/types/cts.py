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

import logging
import logging.handlers

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
        logger.debug('Constructing CTS')

        displayClassName = config.DisplayClassName
        pushButtonMonitorClassName = config.PushButtonMonitorClassName

        displayClass = getattr(hwModule, displayClassName)
        pushButtonMonitorClass = getattr(hwModule, pushButtonMonitorClassName)

        self._display = displayClass(config.Display)
        self._display.setText("Initializing...")

        self._pushButtonMonitor = pushButtonMonitorClass()

        for i in config.PushButtons:
            self._pushButtonMonitor.registerPushButton(i.Name,
                                                       self.buttonPressed,
                                                       i)

        self._submitting = False
        self.ConnectionManager = None

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
        logger.info('CTS transitioned to Processing state.')

        self._combo = Combo(0, 0, 0)

        self._display.setLine1Text("TODO: [Specify starting message here.]")
        self.refreshDisplayedCombo()

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
        logger.debug('Setting display Line 2 to: %s.' % (s))
        self._display.setLine2Text(s)

    # --------------------------------------------------------------------------
    def buttonPressed(self,
                      pushButtonName):
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
        logger.info('Push button %s pressed.' % (pushButtonName))

        if pushButtonName == 'Up':
            self._combo.incCurrentDigit(1)
            self.refreshDisplayedCombo()
            self._submitting = False
        elif pushButtonName == 'Down':
            self._combo.decCurrentDigit(1)
            self.refreshDisplayedCombo()
            self._submitting = False
        elif pushButtonName == 'Left':
            self._combo.moveLeft(1)
            self.refreshDisplayedCombo()
            self._submitting = False
        elif pushButtonName == 'Right':
            self._combo.moveRight(1)
            self.refreshDisplayedCombo()
            self._submitting = False
        elif pushButtonName == 'Enter':
            if self._submitting:
                logger.info('2nd enter key press received. Submitting combo: %s' %
                            (self._combo.toList()))
                # TODO submit combo to MS
                self._submitting = False
            else:
                logger.info('1st enter key press received. Waiting for 2nd.')
                self._submitting = True
        else:
            pass #TODO log unexpected button press received

    # --------------------------------------------------------------------------
    def onFailed(self):
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
        logger.info('CTS transitioned to Failed state.')
        self._display.setText("Failed.")

        self._pushButtonMonitor.stopListening()

    # --------------------------------------------------------------------------
    def onPassed(self):
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
        logger.info('CTS transitioned to Passed state.')
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
        logger.debug('Constructing combo')

        # TODO
        self._position = 0
        self._digits = [0, 0, 0, 0, 0, 0]

        self._digits[0] = value1 / 10 % 10
        self._digits[1] = value1 /  1 % 10
        self._digits[2] = value2 / 10 % 10
        self._digits[3] = value2 /  1 % 10
        self._digits[4] = value3 / 10 % 10
        self._digits[5] = value3 /  1 % 10

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
    def moveLeft(self,
                 numPlaces):
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
        self._position -= 1
        if self._position < 0:
            self._position = len(self._digits) - 1
        logger.debug('moved current combo pos to %s' % (self._position))

    # --------------------------------------------------------------------------
    def moveRight(self,
                  numPlaces):
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
        self._position += 1
        if self._position >= len(self._digits):
            self._position = 0
        logger.debug('moved current combo pos to %s' % (self._position))

    # --------------------------------------------------------------------------
    def incCurrentDigit(self,
                        incrementValue):
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
        value = self._digits[self._position]
        value += 1

        if value > 9:
            value = 0

        self._digits[self._position] = value

    # --------------------------------------------------------------------------
    def decCurrentDigit(self,
                        decrementValue):
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
        value = self._digits[self._position]
        value -= 1

        if value < 0:
            value = 9

        self._digits[self._position] = value

    # --------------------------------------------------------------------------
    def toList(self):
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
        result = [self._digits[0] * 10 + self._digits[1],
                  self._digits[2] * 10 + self._digits[3],
                  self._digits[4] * 10 + self._digits[5]]
        return result

    # --------------------------------------------------------------------------
    def toString(self):
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
        s = ''.join(str(x) for x in self._digits)
        s = s[0:2] + ' ' + s[2:4] + ' ' + s[4:6]
        logger.debug('s = "%s"' % (s))

        idx = self._position
        if idx > 3:
            idx += 2
        elif idx > 1:
            idx += 1

        logger.debug('idx = %s"' % (idx))

        s = s[:idx] + '[' + s[idx] + ']' + s[idx+1:]
        logger.debug('s = "%s"' % (s))

        logger.debug('combo value for (%s, %s, %s) as string: "%s"' %
                     (''.join(str(x) for x in self._digits[0:2]),
                      ''.join(str(x) for x in self._digits[2:4]),
                      ''.join(str(x) for x in self._digits[4:6]),
                      s))

        return s

# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

