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
import sys
from threading import Thread
import time
from time import sleep
from time import time
import traceback

from station.interfaces import IStation


# ------------------------------------------------------------------------------
class Station(IStation):
    """
    TODO class comment
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
        logger.debug('Constructing HMB')

        ledClassName = config.LedClassName
        vibrationMotorClassName = config.VibrationMotorClassName

        ledClass = getattr(hwModule, ledClassName)
        vibrationMotorClass = getattr(hwModule, vibrationMotorClassName)

        self._vibrationMotors = []

        for i in config.VibrationMotors:
            self._vibrationMotors.append(
                VibrationManager(i.Name, i, vibrationMotorClass))

        self._leds = {}

        for i in config.Leds:
            self._leds[i.Name] = ledClass(i.Name, i)

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
        logger.info('Starting HMB.')

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
        logger.info('Received signal "%s". Stopping HMB.', signal)

        for motor in self._vibrationMotors:
            motor.stop()

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
        logger.info('HMB transitioned to Ready state.')

        for motor in self._vibrationMotors:
            motor.stop()

        for name in self._leds.keys():
            self._leds[name].turnOff()

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
        logger.info('HMB transitioned to Processing state with args [%s].' % (args))

        if 2 * len(self._vibrationMotors) == len(args):
            for i, motor in enumerate(self._vibrationMotors):
                onDuration_ms  = args[2*i + 0]
                offDuration_ms = args[2*i + 1]
                onDuration_s   = onDuration_ms  / 1000.0
                offDuration_s  = offDuration_ms / 1000.0
                motor.start(onDuration_s, offDuration_s)

            for name in self._leds.keys():
                self._leds[name].turnOff()

            self._leds['yellow'].turnOn()
        else:
            logger.critical("Mismatched argument length. Cannot start. (num motors = %s, expected num args = %s, actual num args = %s)" % (len(self._vibrationMotors), 2 * len(self._vibrationMotors), len(args)))


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
        logger.info('HMB transitioned to Failed state.')

        for motor in self._vibrationMotors:
            motor.stop()

        for name in self._leds.keys():
            self._leds[name].turnOff()

        self._leds['red'].turnOn()

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
        logger.info('HMB transitioned to Passed state.')

        for motor in self._vibrationMotors:
            motor.stop()

        for name in self._leds.keys():
            self._leds[name].turnOff()

        self._leds['green'].turnOn()

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
        logger.critical('HMB transitioned to Unexpected state %s', value)

        for name in self._leds.keys():
            self._leds[name].setFlashing()


# ------------------------------------------------------------------------------
class VibrationManager:
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 name,
                 config,
                 vibrationMotorClass):
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
        self.Name = name
        logger.debug('Constructing vibration manager %s', self.Name)
        self._timeToExit = False
        self._vibrationMotor = vibrationMotorClass(self.Name, config.OutputPin)
        
        self._currentlyStarted = False
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
        logger.debug('Entering vibration manager %s', self.Name)
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
        logger.debug('Exiting vibration manager %s', self.Name)
        stopListening(self)
        self._timeToExit = True
        self._thread.join()

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
        logger.info('Starting thread for vibration manager %s' % (self.Name))

        lastNotedTime_s = 0
        isVibrating = False
        isMotorOn = False

        while not self._timeToExit:
            try:
                #TODO Delete? logger.debug('Loop begin for vibration manager %s: currently started? %s, transition to started? %s' % (self.Name, self._currentlyStarted, self._transitionToStarted))

                if self._transitionToStarted:
                    if self._currentlyStarted:
                        # no transition - still started
                        pass
                    else:
                        logger.info('Vibration manager %s transition to started' %
                                    (self.Name))
                        self._currentlyStarted = True
                        lastNotedTime_s = time()
                        self._vibrationMotor.start()
                        isVibrating = True
                        isMotorOn = True

                    # started just now or still going
                    if isMotorOn:
                        configDuration_s = self.OnDuration_s
                        motorToggle = self._vibrationMotor.stop
                    else:
                        configDuration_s = self.OffDuration_s
                        motorToggle = self._vibrationMotor.start

                    currentTime_s = time()

                    if lastNotedTime_s + configDuration_s <= currentTime_s:
                        logger.debug('Vibration manager %s toggling motor' % (self.Name))
                        lastNotedTime_s = time()
                        motorToggle()
                        isMotorOn = not isMotorOn

                else:
                    if self._currentlyStarted:
                        logger.info('Vibration manager %s transition to stopped' %
                                    (self.Name))
                        self._currentlyStarted = False
                        lastNotedTime_s = 0
                        self._vibrationMotor.stop()
                        isVibrating = False
                        isMotorOn = False
                    else:
                        # no transition - still not started
                        pass

                    # stopped just now or still stopped - nothing to do

                sleep(1)
            except Exception, e:
                exType, ex, tb = sys.exc_info()
                logger.critical("Exception occurred of type %s in vibration manager %s: %s" % (exType.__name__, self.Name, str(e)))
                traceback.print_tb(tb)

        logger.info('Stopping thread for vibration manager %s' % (self.Name))


    # --------------------------------------------------------------------------
    def start(self,
              onDuration_s,
              offDuration_s):
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
        logger.debug('Starting vibration manager %s', self.Name)
        self.OnDuration_s = onDuration_s
        self.OffDuration_s = offDuration_s
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
        logger.debug('Stopping vibration manager %s', self.Name)
        self._transitionToStarted = False


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

