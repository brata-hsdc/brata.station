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
import sys
from threading import Thread
from threading import Timer
import time
import traceback
from station.util import Config
from station.util import toFloat

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

        try:
            ledClassName = config.LedClassName
            powerOutputClassName = config.PowerOutputClassName
            buzzerClassName = config.BuzzerClassName
            inputClassName = config.InputClassName

            ledClass = getattr(hwModule, ledClassName)
            powerOutputClass = getattr(hwModule, powerOutputClassName)
            buzzerClass = getattr(hwModule, buzzerClassName)
            inputClass = getattr(hwModule, inputClassName)

            self._powerOutputs = {}

            # for now only one but keep design expandable in case
            for i in config.PowerOutputs:
                self._powerOutputs[i.Name] = powerOutputClass(i.Name, i.OutputPin)

            self._leds = {}

            for i in config.Leds:
                self._leds[i.Name] = ledClass(i.Name, i) 

            self._buzzers = {}

            for i in config.Buzzers:
                self._buzzers[i.Name] = buzzerClass(i.Name, i)
                logger.debug('CPA added buzzer named [%s].' % (i.Name))

            self._inputs = {}

            # for now only one but keep design expandable in case
            for i in config.Inputs:
                self._inputs[i.Name] = inputClass(i.Name, i.InputPin)
        except Exception, e:
            exType, ex, tb = sys.exc_info()
            logger.critical("Exception occurred of type %s in cpa init: %s" % (exType.__name__, str(e)))
            traceback.print_tb(tb)

        # TODO is the expired timer common to all stations? 
        # Should both of these be moved up?
        self.expiredTimer = None
        self.ConnectionManager = None

        # All times stored internal to this class are measured in seconds
        self._startTime = 0.0
        self._flashStartTime = 0.0
        self._isRunning = False
        self._isTimeToShutdown = False
        self._correctFlashDetected = False
        self._DISPLAY_LED_BLINK_DURATION = 0.1
        self._ledTimes = {}

        # These defaults will be overriden in the start of onProcessing
        self._maxTimeForCompleteFlash = 10.0
        self._minTimeForFlashStart = 9.0
        self._maxTimeForFlashStart = 9.5
        self._goTimeBeforeFinalLight = 6.0
        self._cpa_pulse_width_s = 0.1
        self._cpa_pulse_width_tolerance_s = 0.01

        self._thread = Thread(target=self.run)
        self._thread.daemon = True # TODO why daemon
        self._thread.start()

    # --------------------------------------------------------------------------
    def __enter__(self):
        logger.debug('Entering CPA')
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
        logger.debug('Exiting CPA')
        self._isTimeToShutdown = True
        self._isRunning = False
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

        while not self._isTimeToShutdown:
          self._flashStartTime = time.time() # fake reset value just to ensure initialized
          self._correctFlashDetected = False
          while self._isRunning:
            try:
                elapsed_time = time.time() - self._startTime
                elapsed_flash_time = time.time() - self._flashStartTime
                # TODO see if can convert inputs to event based in this framework
                if self._inputs['lightDetector'].read() == 1:
                    if elapsed_time < self._minTimeForFlashStart:
                        # flash was too soon
                        logger.info('Flash detected too soon.')
                        self.onFailed(self._correctFlashDetected)
                        break
                    elif self._correctFlashDetected and elapsed_flash_time > self._cpa_pulse_width_s + self._cpa_pulse_width_tolerance_s:
                        logger.info('Flash remained on too long.')
                        self.onFailed(self._correctFlashDetected)
                        break
                    elif (not self._correctFlashDetected) and elapsed_time > self._maxTimeForCompleteFlash:
                        # this is a rising edge past the deadline to start a flash
                        logger.info('Flash detected too late.')
                        self.onFailed(self._correctFlashDetected)
                        break
                    elif not self._correctFlashDetected:
                        # Great they at least hit it at the right time
                        self._correctFlashDetected = True
                        self._flashStartTime = time.time()
                else:
                    # Either should be falling edge or is to long or should not see it yet
                    if self._correctFlashDetected:
                        # This is the falling edge so was it in tollerance
                        if elapsed_flash_time > self._cpa_pulse_width_s - self._cpa_pulse_width_tolerance_s:
                            if elapsed_flash_time < self._cpa_pulse_width_s + self._cpa_pulse_width_tolerance_s:
                                #Success!
                                logger.debug('Elapsed time was %s', elapsed_flash_time)
                                self.onPassed(self._correctFlashDetected)
                                break
                            else:
                                # The flash was too long so fail it, however, indicate
                                # that a hit was detected
                                logger.info('Flash was too long.')
                                logger.debug('Elapsed time was %s', elapsed_flash_time)
                                logger.debug('Max flash width was %s', self._cpa_pulse_width_s + self._cpa_pulse_width_tolerance_s)
                                self.onFailed(self._correctFlashDetected)
                                break
                        else:
                            # The flash was not long enough so fail it, however, indicate
                            # that a hit was detected
                            logger.info('Flash was not long enough.')
                            logger.debug('Elapsed time was %s', elapsed_flash_time)
                            logger.debug('Min flash width was %s', self._cpa_pulse_width_s - self._cpa_pulse_width_tolerance_s)
                            self.onFailed(self._correctFlashDetected)
                            break
                    elif elapsed_time > self._maxTimeForFlashStart:
                        # Too long without a flash
                        logger.info('Flash was not detected in allowed time.')
                        self.onFailed(self._correctFlashDetected)
                        break
                if elapsed_time < self._goTimeBeforeFinalLight + self._DISPLAY_LED_BLINK_DURATION and self._nextLed < 16:
                    # The series of LEDs '0' to ending with last light '15'
                    logger.debug('nextLED = %s', self._nextLed )
                    if self._nextLed < 16 and self._ledTimes[str(self._nextLed)] >= elapsed_time:
                        # time to set it off
                        self._leds[str(self._nextLed)].turnOn() # TODO change to fade once that works
                        self._nextLed = self._nextLed + 1
                        logger.debug('nextLED = %s', self._nextLed)

                time.sleep(0.001)
            except Exception, e:
                exType, ex, tb = sys.exc_info()
                logger.critical("Exception occurred of type %s in CPA run" % (exType.__name__))
                logger.critical(str(e))
                traceback.print_tb(tb)

          self._isRunning = False
          time.sleep(0.001) # wait to start again or exit

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
        if self._isRunning:
            # Need to stop the thread first
            self._isRunning = False
            self._thread.join()
        self._correctFlashDetected = False
        for name in self._leds.keys():
            self._leds[name].turnOff()
        for name in self._powerOutputs.keys():
            self._powerOutputs[name].stop()
        for name in self._buzzers.keys():
            self._buzzers[name].off()

        # Report time out TODO I thought this was the same as fail?
        if self.ConnectionManager != None:
            self.ConnectionManager.timeExpired()


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

        # args = [cpa_velocity(tbd change this), cpa_velocity_tolerance_ms(tbd remove), 
        # cpa_window_time_ms, cpa_window_time_tolerance_ms, 
        # cpa_pulse_width_ms, cpa_pulse_width_tolerance_ms]

        # TODO rework indexing if change arguments
        # would be nice if these were named value pairs but for now 
        # follow the existing design
        if 6 == len(args):
            # time to flash the last light before the laser should come
            self._goTimeBeforeFinalLight = toFloat(args[0], 0.0) / 1000.0
            # there are 16 blocks of time before the last light so find intervals for each light
            for i in range(16):
                 self._ledTimes[str(i)]=((1.0+i)*self._goTimeBeforeFinalLight/16.0)
                 logger.debug('time %s = %s', i, self._ledTimes[str(i)])

            # set up for the first LED
            self._nextLed = 0

            # earliest possible time a start of a flash would be acceptable
            self._minTimeForFlashStart = (toFloat(args[2], 0.0)-toFloat(args[3], 0.0)) / 1000.0

            # the absolute latest time you could start a flash and still finish it within tolerance of the shortest flash duration
            self._maxTimeForFlashStart = (toFloat(args[2], 0.0)+toFloat(args[3], 0.0)-toFloat(args[4], 0.0)+toFloat(args[5], 0.0)) / 1000.0
            self._maxTimeForCompleteFlash = (toFloat(args[2], 0.0)+toFloat(args[3], 0.0)) / 1000.0
            self._cpa_pulse_width_s = toFloat(args[4], 0.0) / 1000.0
            self._cpa_pulse_width_tolerance_s = toFloat(args[5], 0.0) / 1000.0
            self._isRunning = False
            self._correctFlashDetected = False
            for name in self._leds.keys():
                self._leds[name].turnOff()
            for name in self._powerOutputs.keys():
                self._powerOutputs[name].start()
            for name in self._buzzers.keys():
                self._buzzers[name].off()
            self._leds['red'].turnOn()
            self._buzzers['red'].playSynchronously()
            self._leds['red'].turnOff()
            self._leds['yellow'].turnOn()
            self._buzzers['yellow'].playSynchronously()
            self._leds['yellow'].turnOff()
            self._leds['green'].turnOn()
            self._startTime = time.time()
            self._isRunning = True
            self._buzzers['green'].playSynchronously()
            self._leds['green'].turnOff()

        else:
            logger.critical('Mismatched argument length. Cannot start.')

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

        # Reset inputs and outputs
        for name in self._leds.keys():
            self._leds[name].turnOff()
        for name in self._powerOutputs.keys():
            self._powerOutputs[name].stop()
        for name in self._buzzers.keys():
            self._buzzers[name].off()
        self._leds['red'].turnOn()

        # Inform the Master Server this event failed
        if self.ConnectionManager != None:
            failArgs = []
            arg1 = Config()
            arg1.Name = 'hit_detected_within_window'
            arg1.Value = args
            failArgs.append(arg1)
            arg2 = Config()
            arg2.Name = 'is_correct'
            arg2.Value = 'False'
            failArgs.append(arg2)
            self.ConnectionManager.submitToMS(failArgs)

        self._buzzers['FailBuzzer'].playSynchronously()
        self._leds['red'].turnOff()

    # --------------------------------------------------------------------------
    def onPassed(self,
                 args):
        """TODO title and figure out why args is needed

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

        # Reset inputs and outputs
        for name in self._leds.keys():
            self._leds[name].turnOff()
        for name in self._powerOutputs.keys():
            self._powerOutputs[name].stop()
        for name in self._buzzers.keys():
            self._buzzers[name].off()
        self._leds['green'].turnOn()

        # Inform the Master Server this event passed
        if self.ConnectionManager != None:
            passArgs = []
            arg1 = Config()
            arg1.Name = 'hit_detected_within_window'
            arg1.Value = 'True'
            passArgs.append(arg1)
            arg2 = Config()
            arg2.Name = 'is_correct'
            arg2.Value = 'True'
            passArgs.append(arg2)
            self.ConnectionManager.submitToMS(passArgs)

        self._buzzers['SuccessBuzzer'].playSynchronously()
        self._leds['green'].turnOff()

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

        for name in self._leds.keys():
            self._leds[name].setFlashing()

# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address='/dev/log')
logger.addHandler(handler)

