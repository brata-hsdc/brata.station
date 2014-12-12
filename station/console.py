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

from collections import namedtuple
import logging
import logging.handlers
import sys
from threading import Thread
from time import sleep
import traceback

from station.interfaces import IDisplay
from station.interfaces import ILed
from station.interfaces import IPushButtonMonitor
from station.interfaces import IVibrationMotor
from station.util import NonBlockingConsole


# ------------------------------------------------------------------------------
class Display(IDisplay):
    """
    TODO class comment
    """

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
        logger.debug('Entering display')
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
        logger.debug('Exiting display')
        self.setText('')

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
        logger.debug('Setting background color to %s' % (color))
    

    # --------------------------------------------------------------------------
    def setLine1Text(self,
                     text):
        """Sets the text for line 1 of the display.

        Sets the text for line 1 of the display. If the text is too long to fit
        on the display, then the text scrolls over time.

        Args:
            text (string): The text to display.
        Returns:
            N/A.
        Raises:
            N/A.

        """
        self._line1Text = text
        logger.debug('Setting Line 1 text. Display now reads "%s"[br]"%s"' %
                     (self._line1Text, self._line2Text))


    # --------------------------------------------------------------------------
    def setLine2Text(self,
                     text):
        """Sets the text for line 2 of the display.

        Sets the text for line 2 of the display. If the text is too long to fit
        on the display, then the text scrolls over time.

        Args:
            text (string): The text to display.
        Returns:
            N/A.
        Raises:
            N/A.

        """
        self._line2Text = text
        logger.debug('Setting Line 2 text. Display now reads "%s"[br]"%s"' %
                     (self._line1Text, self._line2Text))


    # --------------------------------------------------------------------------
    def setText(self,
                text):
        """Sets the text for the entire display.

        Directly sets the text for the display. Multiple lines can be provided
        at once by separating with a '\n' character.

        Args:
            text (string): The text to display.
        Returns:
            N/A.
        Raises:
            N/A.

        """
        idx = text.find('\n')

        if idx != -1:
            self._line1Text = text[:idx]
            self._line2Text = text[idx+1:]
        else:
            self._line1Text = text
            self._line2Text = ''

        logger.debug('Setting Line 2 text. Display now reads "%s"[br]"%s"' %
                     (self._line1Text, self._line2Text))


    # --------------------------------------------------------------------------
    def showCursor(self, show=True):
        """ Shows or hides the cursor.
        
        Make the cursor visible if show is True.  Otherwise, make the cursor
        invisible.
        """
        logger.debug('Setting show cursor value to %s' % (show))

        
    # --------------------------------------------------------------------------
    def setCursor(self, row=0, col=0):
        """ Sets the position of the cursor and makes it visible.
        """
        logger.debug('Setting cursor position to (r=%s, c=%s)' % (row, col))

        
# ------------------------------------------------------------------------------
class Led(ILed):
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 name,
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
        self.Name = name + " (" + config.OutputPin +")"
        logger.debug('Constructing LED %s', self.Name)

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
        logger.debug('Entering LED %s', self.Name)
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
        logger.debug('Exiting LED %s', self.Name)
        self.turnOff()

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
        logger.debug('Turning off LED %s', self.Name)

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
        logger.debug('Turning on LED %s', self.Name)

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
        logger.debug('Set LED %s flashing', self.Name)


# ------------------------------------------------------------------------------
PushButton = namedtuple('PushButton', 'Name Handler')


# ------------------------------------------------------------------------------
class PushButtonMonitor(IPushButtonMonitor):
    """
    TODO class comment
    """

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
        self._pushButtons = {}
        self._listening = False
        self._timeToExit = False
        self._thread = Thread(target = self.run)
        self._thread.daemon = True
        self._thread.start()

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
        keypress = config.ConsoleKeyPress

        if keypress in self._pushButtons:
            logger.warning('Console key [%s] already registered to push button %s; redefining to register to push button %s' %
                           (keypress, self._pushButtons[keypress].Name, name))

        self._pushButtons[keypress] = PushButton(name, buttonPressHandler)

        logger.debug('Registered push button %s for key press [%s]' %
                     (name, keypress))

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
                        keypress = nbc.get_data()

                        if keypress in self._pushButtons:
                            pb = self._pushButtons[keypress]

                            logger.debug('Received key press event [%s] from push button monitor for push button %s' % (keypress, pb.Name))
                            pb.Handler(pb.Name)

                        elif keypress != False:
                            logger.warning('Received unexpected key press event for <%s> from push button monitor' % (keypress))

                        # ignore all other key presses
                        else:
                            pass

                    sleep(0.1)
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
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        self.Name = name + " (" + outputPin +")"

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


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

