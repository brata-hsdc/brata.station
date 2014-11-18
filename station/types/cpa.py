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
        buzzerClassName = config.BuzzerClassName
        inputClassName = config.InputClassName

        ledClass = getattr(hwModule, ledClassName)
        powerOutputClass = getattr(hwModule, powerOutputClassName)
        buzzerClass = getattr(hwModule, buzzerClassName)
        inputClass = getattr(hwModule, InputClassName)

        self._powerOutputs = {}

        # for now only one but keep design expandable in case
        for i in config.PowerOutputs:
            self._powerOutputs[i.Name] = powerOutputClass(i.Name, i.OutputPin)

        self._leds = {}

        for i in config.Leds:
            self._leds[i.Name] = ledClass(i.Name, i) # TODO: SS - Should I be placing the color from the config file here?

        self._buzzers = {}

        for i in config.Buzzers:
            self._buzzers[i.Name] = buzzerClass(i.Name, i)

        self._inputs = {}

        # for now only one but keep design expandable in case
        for i in config.Inputs:
            self._inputs[i.Name] = inputClass(i.Name, i.InputPin)

         # TODO is the expired timer common to all stations? Should both of these be moved up?
        self.expiredTimer = None
        self.ConnectionManager = None

        # All times stored internal to this class are measured in seconds
        self._startTime = 0.0
        self._flashStartTime = 0.0
        self._isRunning = False
        self._correctFlashDetected = False
        self._DISPLAY_LED_BLINK_DURATION = 0.1

	# These defaults will be overriden in the start of onProcessing
        self._maxTimeForCompleteFlash = 10.0
        self._minTimeForFlashStart = 9.0
        self._goTimeBeforeFinalLight = 6.0
        self._cpa_pulse_width_s = 0.1
        self._cpa_pulse_width_tolerance_s = 0.01

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
        while self._isRunning:
           try:  
              elapsed_time = time.time() - self._startTime
              # TODO see if can convert inputs to event based in this framework
              if self._inputs['lightDetector'].read() == 1:
                 if elapsed_time < self._minTimeForFlashStart:
                    # flash was too soon
                    logger.info('Flash detected too soon.')
                    self.onFailed(self._correctFlashDetected)
                 elif elapsed_time > self.maxTimeForCompleteFlash:
                    # in theory time out logic should have caught this by now
                    # but as written this is currently a race condition
                    # TODO as we are running this without events should get rid
                    # of the timer and just catch this case for reporting?
                 else:
                    # Great they at least hit it at the right time
                    self._correctFlashDetected = True
                    self._flashStartTime = time.time()
              else:
                 # Either should be falling edge or is to long or should not see it yet
                 if self._correctFlashDetected:
                    # This is the falling edge so was it in tollerance
                    elapsed_flash_time = time.time() - self._flashStartTime
                    if elapsed_flash_time > self._cpa_pulse_width_s - self._cpa_pulse_width_tolerance_s:
                       if elapsed_flash_time < self._cpa_pulse_width_s + self._cpa_pulse_width_tolerance_s:
                          #Success!
                          self.onPassed(self._correctFlashDetected)
                       else
                          # The flash was too long so fail it, however, indicate
                          # that a hit was detected
                          logger.info('Flash was too long.')
                          self.onFailed(self._correctFlashDetected)
                    else
                       # The flash was not long enough so fail it, however, indicate
                       # that a hit was detected
                       logger.info('Flash was not long enough.')
                       self.onFailed(self._correctFlashDetected)
                 elif elapsed_time > self.minTimeForFlashStart:
                    # Too long without a flash
                    logger.info('Flash was not detected in time.')
                    self.onFailed(self._correctFlashDetected)

              if elapsed_time > self._goTimeBeforeFinalLight and elapsed_time < self._goTimeBeforeFinalLight + self._DISPLAY_LED_BLINK_DURATION:
                 # TODO this needs to be replaced with the series of LEDs ending with last light
                 self._leds['green'].turnOn()
                 time.sleep(self._DISPLAY_LED_BLINK_DURATION)
                 self._leds['green'].turnOff()

              time.sleep(0.001)
           except Exception, e:
              exType, ex, tb = sys.exc_info()
              logger.critical("Exception occurred of type %s in CPA run" % (exType.__name__))
              logger.critical(str(e))
              traceback.print_tb(tb)
      
        self._isRunning = False

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
           self._goTimeBeforeFinalLight = args[0] / 1000.0
           self._minTimeForFlashStart = (args[2]-args[3]) / 1000.0
           self._maxTimeForCompleteFlash = (args[2]+args[3]) / 1000.0
           self._cpa_pulse_width_s = (args[4]) / 1000.0
           self._cpa_pulse_width_tolerance_s = (args[5]) / 1000.0
           self._currentlyStarted = False
           self._correctFlashDetected = False
           for name in self._leds.keys():
              self._leds[name].turnOff()
           for name in self._powerOutputs.keys():
              self._powerOutputs[name].start()
           for name in self._buzzers.keys():
              self._buzzers[name].off()
           self._leds['red'].turnOn()
           self._buzzers['SuccessBuzzer'].note(0)
           time.sleep(1)
           self._leds['red'].turnOff()
           self._leds['yellow'].turnOn()
           self._buzzers['SuccessBuzzer'].note(1)
           time.sleep(1)
           self._leds['yellow'].turnOff()
           self._leds['green'].turnOn()
           self._buzzers['SuccessBuzzer'].note(2)
           self._startTime = time.time();
           self._currentlyStarted = True
           self.expiredTimer = Timer(self._maxTimeForCompleteFlash, self.onTimeExpired)
           self.expiredTimer.start()
           self._thread = Thread(target = self.run)
           self._thread.daemon = True
           self._thread.start()
           time.sleep(1)
           self._leds['green'].turnOff()
           self._buzzers['SuccessBuzzer'].off()
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
        if self._isRunning:
           # Need to stop the thread first
           self._isRunning = False
           self._thread.join()
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
        if self._isRunning:
           # Need to stop the thread first
           self._isRunning = False
           self._thread.join()
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

        self._buzzers['SuccessBuzzer'].playSyncrhonously()
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

