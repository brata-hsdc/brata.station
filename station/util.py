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
Provides general utilities.
"""

import logging
import logging.handlers
import select
import sys
import termios
import tty


# ------------------------------------------------------------------------------
class Config(object):
   pass

# --------------------------------------------------------------------------
def toFloat(floatString, defaultValueOnException):
    """Safely return an int from a string and if not default the value.

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

    returnValue = defaultValueOnException
    try:
        returnValue = float(floatString)
    except ValueError, e:
        exType, ex, tb = sys.exc_info()
        logger.critical("String %s could not be converted to a float" % floatString)
        logger.critical("Defaulting to value of %s" % defaultValueOnException)
        logger.critical(str(e))
        traceback.print_tb(tb)

    return returnValue

# --------------------------------------------------------------------------
def toInt(integerString, defaultValueOnException):
    """Safely return an int from a string and if not default the value.

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

    try:
        return int(integerString)
    except ValueError, e:
        exType, ex, tb = sys.exc_info()
        logger.critical("Exception occurred of type %s in %s" % (exType.__name__))
        logger.critical(str(e))
        traceback.print_tb(tb)
    return defaultValueOnException

# ------------------------------------------------------------------------------
def gcd(a, b):
    """Return greatest common divisor using Euclid's Algorithm."""
    while b:      
        a, b = b, a % b
    return a

# ------------------------------------------------------------------------------
def lcm(a, b):
    """Return lowest common multiple."""
    return a * b // gcd(a, b)

# ------------------------------------------------------------------------------
def lcmm(*args):
    """Return lcm of args."""   
    return reduce(lcm, args)

# ------------------------------------------------------------------------------
class NonBlockingConsole(object):
    """
    Provides support for capturing keyboard input without blocking the console.
    This means the get_data method will not block while waiting for input, so
    the surrounding application can still continue if no key press is detected.

    Example usage:

        with NonBlockingConsole() as nbc:
            while True:
                keypress = nbc.get_data()

                if keypress == ' ':
                    processSpace()

                # ignore all other key presses
                else:
                    pass
    """

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
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
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
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    # --------------------------------------------------------------------------
    def get_data(self):
        """Returns a key press if one was detected

        If a key press was detected, then the key is returned; otherwise, the
        method returns with another indicator. This method does not block on
        input.

        Args:
            N/A
        Returns:
            the key press character
        Raises:
            N/A

        """
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
        return False


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

