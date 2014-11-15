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
Provides the definitions needed for the CPA station type.
"""

import logging
import logging.handlers
import time

from station.interfaces import IStation


# ------------------------------------------------------------------------------
class Station(IStation):
    """
    Provides the implementation for a CPA station to support TODO.
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
        logger.debug('Constructing CPA')

        # TODO - Jaron add code here
        ledClassName = config.LedClassName
        powerOutputClassName = config.PowerOutputClassName

        ledClass = getattr(hwModule, ledClassName)
        powerOutputClass = getattr(hwModule, powerOutputClassName)

        self._powerOutputs = {}

        # for now only one but keep design expandable in case
        for i in config.PowerOutputs:
            self._powerOutputs[i.Name] = powerOutputClass(i.Name, i.OutputPin)

        self._leds = {}

        for i in config.Leds:
            self._leds[i.Name] = ledClass(i.Name, i) # TODO: SS - Should I be placing the color from the config file here?

         # TODO is the expired timer common to all stations? Should both of these be moved up?
        self.expiredTimer = None
        self.ConnectionManager = None

        # All times stored internal to this class are measured in seconds
        self._startTime = 0
        self._currentlyStarted = False
        self._correctFlashDetected = False
        self._LIGHT_FLASH_DURATION = 0.1

	# These defaults will be overriden in the start of onProcessing
        self._maxTimeForCompleteFlash = 10
        self._minTimeForFlashStart = 9
        self._goTimeBeforeFinalLight = 6

    # --------------------------------------------------------------------------
    @property
    def stationTypeId(self):
        """Identifies this station's type as CPA.

        Args:
            N/A.
        Returns:
            N/A.
        Raises:
            N/A.

        """
        return "CPA"

    # --------------------------------------------------------------------------
    def start(self):
        """Set the CPA challenge to the ready state

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
        logger.info('Starting CPA.')

        # TODO - Jaron add code here

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
        logger.info('Received signal "%s". Stopping CPA.', signal)

        # TODO - Jaron add code here

    # --------------------------------------------------------------------------
    def onReady(self):
        """Reset to the state to be ready to start the challenge.

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
        logger.info('CPA transitioned to Ready state.')

        # TODO - Jaron add code here

    # --------------------------------------------------------------------------
    def onProcessing(self,
                     args):
        """Start the challenge. Game on!

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
        logger.info('CPA transitioned to Processing state with args [%s].' % (args))

        # TODO - Jaron add code here
        # args = [cpa_velocity(tbd change this), cpa_velocity_tolerance_ms(tbd remove), 
        # cpa_window_time_ms, cpa_window_time_tolerance_ms, 
        # cpa_pulse_width_ms, cpa_pulse_width_tolerance_ms]

        # TODO rework indexing if change arguments
        # would be nice if these were named value pairs but for now 
        # follow the existing design
        if 6 = len(args):
           self._goTimeBeforeFinalLight = args[0] / 1000
           self._minTimeForFlashStart = (args[2]-args[3]) / 1000
           self._maxTimeForCompleteFlash = (args[2]+args[3]) / 1000
           self._currentlyStarted = False
           self._correctFlashDetected = False
           for name in self._leds.keys():
              self._leds[name].turnOff()
           for name in self._powerOutputs.keys():
              self._powerOutputs[name].start()
           self._leds['red'].turnOn()
           pibrella.buzzer.note(0)
           time.sleep(1)
           self._leds['red'].turnOff()
           self._leds['yellow'].turnOn()
           pibrella.buzzer.note(1)
           time.sleep(1)
           self._leds['yellow'].turnOff()
           self._leds['green'].turnOn()
           pibrella.buzzer.note(2)
           self._startTime = time.time();
           self._currentlyStarted = True
           self.expiredTimer = Timer(self._maxTimeForCompleteFlash, self.onTimeExpired)
           self.expiredTimer.start()
           time.sleep(1)
           self._leds['green'].turnOff()
           pibrella.buzzer.off()
        else:
            logger.critical("Mismatched argument length. Cannot start.")

    # --------------------------------------------------------------------------
    def onTimeExpired(self):
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
        logger.info('CPA time expired.')

        # Reset
        self._currentlyStarted = False
        self._correctFlashDetected = False
        for name in self._leds.keys():
           self._leds[name].turnOff()
        for name in self._powerOutputs.keys():
           self._powerOutputs[name].stop()

        # Report time out TODO I thought this was the same as fail?
        if self.ConnectionManager != None:
            self.ConnectionManager.timeExpired()

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
        logger.info('CPA transitioned to Failed state with args [%s].' % (args))

        # TODO - Jaron add code here
        for name in self._leds.keys():
            self._leds[name].turnOff()

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
        logger.info('CPA transitioned to Passed state with args [%s].' % (args))

        # TODO - Jaron add code here
        for name in self._leds.keys():
            self._leds[name].turnOff()

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
        logger.critical('CPA transitioned to Unexpected state %s', value)

        # TODO - Jaron add code here
        for name in self._leds.keys():
            self._leds[name].setFlashing()

# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

