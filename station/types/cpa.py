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
sys.path.append('/user/lib/python2.7/dist-packages')
import pygame

# ------------------------------------------------------------------------------
class Station(IStation):
    """
    Provides the implementation for a CPA station to support TODO.
    """
    def waitDone(self):
      while pygame.mixer.music.get_busy() == True:
        pass

    def waitForBusy(self):
      while pygame.mixer.music.get_busy() == False:
        pass

    def playCountdown(self, val):
      try:
        wait = True
        if self._countDownToggle:
          if val > 2:
            led='red'
            pygame.mixer.music.load('/opt/designchallenge2015/brata.station/bin/Tone_1000_500ms.wav')
          elif val == 2:
            # This really should be a separate tone but mike wants the same
            led='yellow'
            pygame.mixer.music.load('/opt/designchallenge2015/brata.station/bin/Tone_1000_500ms.wav')
          if val < 2:
            # This play must be asynchronous or the timing will be messed up
            wait = False
            led='green'
            pygame.mixer.music.load('/opt/designchallenge2015/brata.station/bin/Tone_2000_500ms.wav')
            self._countDownToggle =  not self._countDownToggle
          self._leds[led].turnOn()
          pygame.mixer.music.play()
          if wait:
            self.waitDone()
            self._leds[led].turnOff()
            time.sleep(0.5)
        else:
          if val > 2:
            led='red'
          elif val == 2:
            led='yellow'
          if val < 2:
            # This play must be asynchronous or the timing will be messed up
            wait = False
            led='green'
            self._countDownToggle =  not self._countDownToggle
          self._leds[led].turnOn()
          if wait:
            self._buzzers[led].playSynchronously()
            self._leds[led].turnOff()
          else:
            self._buzzers[led].play()
      except Exception, e:
        exType, ex, tb = sys.exc_info()
        logger.critical("Exception occurred of type %s in cpa playCountdown: %s" % (exType.__name__, str(e)))
        traceback.print_tb(tb)

    def playCount(self):
      try:
        pygame.mixer.quit()
        pygame.mixer.init(frequency=8000, buffer=512)
        pygame.mixer.music.load('/opt/designchallenge2015/brata.station/bin/countdown.wav')
        time.sleep(3)
        pygame.mixer.music.play()
        self.waitForBusy()
      except Exception, e:
          exType, ex, tb = sys.exc_info()
          logger.critical("Exception occurred of type %s in cpa playBond: %s" % (exType.__name__, str(e)))
          traceback.print_tb(tb)

    def playBond(self):
      try:
        pygame.mixer.quit()
        pygame.mixer.init()
        pygame.mixer.music.load('/opt/designchallenge2015/brata.station/bin/bond_theme.wav')
        pygame.mixer.music.play()
        self.waitDone()  
      except Exception, e:
          exType, ex, tb = sys.exc_info()
          logger.critical("Exception occurred of type %s in cpa playBond: %s" % (exType.__name__, str(e)))
          traceback.print_tb(tb)

    def playFail(self):
      try:
        pygame.mixer.music.load('/opt/designchallenge2015/brata.station/bin/uh_oh.wav')
        pygame.mixer.music.play()
        self.waitDone()  
      except Exception, e:
          exType, ex, tb = sys.exc_info()
          logger.critical("Exception occurred of type %s in cpa playFail: %s" % (exType.__name__, str(e)))
          traceback.print_tb(tb)

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

            for name in self._powerOutputs.keys():
              if name != "LaserWindow":
                self._powerOutputs[name].start()
                msg = 'Enabled power output %s' %(name)
                logger.info(msg)
          

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
        self._DISPLAY_LED_BLINK_DURATION = 0.1

        self._isRunning = False
        self._isTimeToShutdown = False
        self._correctFlashDetected = False
        self._wasButtonPressed = False
        self._attemptCount = 0
        self._MAX_ATTEMPTS = 3
        self._isNewStartOrRetry = True

        # These defaults will be overriden in the start of onProcessing
        self._maxTimeForCompleteFlash = 10.0
        self._minTimeForFlashStart = 9.0
        self._maxTimeForFlashStart = 9.5
        self._goTimeBeforeFinalLight = 6.0
        self._cpa_pulse_width_s = 0.1
        self._cpa_pulse_width_tolerance_s = 0.01
        self._ledTimes = {}
        self._ledDecay = 0.1
        self._theatric_delay_s = 2.0
 
        self._countDownToggle = True

        self._thread = Thread(target=self.run)
        #self._thread.daemon = True # TODO why daemon
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
        for name in self._powerOutputs.keys():
            self._powerOutputs[name].stop()
        # This did not appear to be called but stop was so moved all clean up
        # to stop

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
          while self._isRunning:
            if self._isNewStartOrRetry:
              logger.debug('CPA is setting up for a new run')
              # Need to add theatrical delay
              time.sleep(self._theatric_delay_s)
              # Need to reinitialize everything and increase attempt count
              self._correctFlashDetected = False
              self._attemptCount = self._attemptCount + 1
              msg = ''
              # A bit of extra detailed logging flags to see how off we are
              windowIsOpenNotReported = True
              # set up for the first LED
              self._nextLed = 0
              self._correctFlashDetected = False
              for name in self._leds.keys():
                self._leds[name].turnOff()
              for name in self._buzzers.keys():
                self._buzzers[name].off()
              self.playCount()
              self._leds['red'].turnOn()
              time.sleep(0.5)
              self._leds['red'].turnOff()
              time.sleep(0.5)
              self._leds['red'].turnOn()
              time.sleep(0.5)
              self._leds['red'].turnOff()
              time.sleep(0.5)
              self._leds['yellow'].turnOn()
              time.sleep(0.5)
              self._leds['yellow'].turnOff()
              time.sleep(0.5)
              self._leds['green'].turnOn()
              #self.playCountdown(3)
              #self.playCountdown(3)
              #self.playCountdown(2)
              # This play must be asynchronous or the timing will be messed up
              #self.playCountdown(1)
              self._startTime = time.time()
              #self._leds['green'].turnOff()
              self._isNewStartOrRetry = False
            try:
                elapsed_time = time.time() - self._startTime
                elapsed_flash_time = time.time() - self._flashStartTime
                # TODO see if can convert inputs to event based in this framework
                if self._inputs['lightDetector'].read() == 1:
                    if elapsed_time < self._minTimeForFlashStart:
                        # flash was too soon
                        msg = 'Flash detected too soon. Elapsed time was %s. Should not start before %s.' %(elapsed_time, self._minTimeForFlashStart)
                        logger.info(msg)
                        self.onFailed(self._correctFlashDetected, msg)
                        break
                    elif self._correctFlashDetected and elapsed_flash_time > self._cpa_pulse_width_s + self._cpa_pulse_width_tolerance_s:
                        msg = 'Flash remained on too long. Duration was %s. Allowed duration including tolerance is %s.' %(elapsed_flash_time, self._cpa_pulse_width_s + self._cpa_pulse_width_tolerance_s)
                        logger.info(msg)
                        self.onFailed(self._correctFlashDetected, msg)
                        break
                    elif (not self._correctFlashDetected) and elapsed_time > self._maxTimeForCompleteFlash:
                        # this is a rising edge past the deadline to start a flash
                        msg = 'Flash detected too late. Elapsed time was %s. Flash required to be complete by %s.' %(elapsed_time, self._maxTimeForCompleteFlash) 
                        logger.info(msg)
                        self.onFailed(self._correctFlashDetected, msg)
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
                                msg = 'You captured PA at %s with flash duration of %s.' %(elapsed_time,elapsed_flash_time)
                                logger.debug(msg)
                                self.onPassed(msg)
                                break
                            else:
                                # The flash was too long so fail it, however, indicate
                                # that a hit was detected
                                msg = 'Flash was too long. '
                                msg = msg + 'Elapsed time was %s, but ' %(elapsed_flash_time)
                                msg = msg + 'max flash width is %s.' %(self._cpa_pulse_width_s + self._cpa_pulse_width_tolerance_s)
                                logger.debug(msg)
                                self.onFailed(self._correctFlashDetected, msg)
                                break
                        else:
                            # The flash was not long enough so fail it, however, indicate
                            # that a hit was detected
                            msg = 'Flash was not long enough. '
                            msg = msg + 'Elapsed time was %s, but ' %(elapsed_flash_time)
                            msg = msg + 'min flash width is %s.' %(self._cpa_pulse_width_s - self._cpa_pulse_width_tolerance_s)
                            self.onFailed(self._correctFlashDetected, msg)
                            break
                    elif elapsed_time > self._maxTimeForFlashStart:
                        # Too long without a flash
                        msg = 'Flash was not detected in allowed time. '
                        msg = msg + 'Elapsed time was %s, but must have started by %s.' %(elapsed_time, self._maxTimeForFlashStart)
                        self.onFailed(self._correctFlashDetected, msg)
                        break
                if elapsed_time < self._goTimeBeforeFinalLight or self._nextLed == 15:
                    # The series of LEDs '0' to ending with last light '15'
                    if self._nextLed < 16 and self._ledTimes[str(self._nextLed)] <= elapsed_time:
                        # time to set it off
                        # self._leds[str(self._nextLed)].fade(100,0,self._ledDecay)
                        self._leds[str(self._nextLed)].turnOn()
                        #logger.debug('nextLED = %s nextTime = %s elapsed = %s' %(self._nextLed, self._ledTimes[str(self._nextLed)], elapsed_time) )
                        self._nextLed = self._nextLed + 1

                #time.sleep(0.001)
                if self._nextLed >= 0:
                  # Yes this could be optimized down but leaving needless calls for consistent timing
                  # this is to ensure it appears a constant velocity
                  for j in range(15, -1, -1):
                    self._leds[str(j)].decay()
                #logger.debug('elapsed = %s' %(elapsed_time) )

                if windowIsOpenNotReported and elapsed_time > self._minTimeForFlashStart:
                  self._powerOutputs["LaserWindow"].start()
                  logger.debug('Window opened at %s should have been %s' %(elapsed_time,self._minTimeForFlashStart) )
                  windowIsOpenNotReported = False

            except Exception, e:
                exType, ex, tb = sys.exc_info()
                logger.critical("Exception occurred of type %s in CPA run" % (exType.__name__))
                logger.critical(str(e))
                traceback.print_tb(tb)

          time.sleep(0.001) # wait to start again or exit

        logger.debug('CPA main thread finished')

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
        self._isTimeToShutdown = True
        self._isRunning = False
        self._thread.join()
        logger.info('CPA after thread join.')
        for name in self._buzzers.keys():
           self._buzzers[name].stop()
        for name in self._leds.keys():
            self._leds[name].stop()

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
        # cpa_pulse_width_ms, cpa_pulse_width_tolerance_ms, theatric_delay_ms]

        # TODO rework indexing if change arguments
        # would be nice if these were named value pairs but for now 
        # follow the existing design
        if 7 == len(args):
            # Make sure is not running before tweaking params
            if self._isRunning:
              # Then we have a problem as MS did not wait for us to send 
              # notification that we finished the last set of runs
              self._isRunning = False
              # Current logic doesn't ensure it stopped,
              # but at the same time can't hold up response to master server
              # until come up with something better try to give some time 
              # to abort the last run in whatever state it is in
              time.sleep(0.1) # don't wait too long or MS may assume we died
  
            # reset to try up to max times as the MS directed this start
            self._attemptCount = 0

            # Set all the new parameters from MS for this new trial set
            # time to flash the last light before the laser should come
            self._goTimeBeforeFinalLight = toFloat(args[0], 0.0) / 1000.0
            logger.debug('goTimeBeforeFinalLight = %s', self._goTimeBeforeFinalLight)

            # there are 15 blocks of time before the last light so find intervals for each light
            # note this is because timing starts at the first of the 16 lights
            for i in range(16):
                 self._ledTimes[str(i)]=((i)*self._goTimeBeforeFinalLight/15.0)
                 logger.debug('time %s = %s', i, self._ledTimes[str(i)])

            # Use 2x the time interval for the decay /15*2 same as / 7.5
            self._ledDecay = self._goTimeBeforeFinalLight/7.5

            # earliest possible time a start of a flash would be acceptable
            self._minTimeForFlashStart = (toFloat(args[2], 0.0)-toFloat(args[3], 0.0)) / 1000.0
            logger.debug('minTimeForFlashStart = %s', self._minTimeForFlashStart)

            # the absolute latest time you could start a flash and still finish it within tolerance of the shortest flash duration
            self._maxTimeForFlashStart = (toFloat(args[2], 0.0)+toFloat(args[3], 0.0)-toFloat(args[4], 0.0)+toFloat(args[5], 0.0)) / 1000.0
            logger.debug('maxTimeForFlashStart = %s', self._maxTimeForFlashStart)
            self._maxTimeForCompleteFlash = (toFloat(args[2], 0.0)+toFloat(args[3], 0.0)) / 1000.0
            logger.debug('maxTimeForCompleteFlash = %s', self._maxTimeForCompleteFlash)
            self._cpa_pulse_width_s = toFloat(args[4], 0.0) / 1000.0
            logger.debug('cpa_pulse_width_s = %s', self._cpa_pulse_width_s)
            self._cpa_pulse_width_tolerance_s = toFloat(args[5], 0.0) / 1000.0
            logger.debug('cpa_pulse_width_tolerance_s  = %s', self._cpa_pulse_width_tolerance_s )

            # set the theatric delay
            self._theatric_delay_s = (toFloat(args[6], 0.0)) / 1000.0
            logger.debug('theatric_delay_s = %s', self._theatric_delay_s)

            self._isRunning = True
            logger.debug('CPA is running')

        else:
            logger.critical('Mismatched argument length. Cannot start.')

    # --------------------------------------------------------------------------
    def onFailed(self,
                 hitDetected,
                 failMessage):
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
        logger.info('CPA transitioned to Failed state with args hitDetected=%s failMessage=%s.' %(hitDetected, failMessage))

        # Reset inputs and outputs
        self._powerOutputs["LaserWindow"].stop()
        for name in self._leds.keys():
            self._leds[name].turnOff()
        for name in self._buzzers.keys():
            self._buzzers[name].off()
        self._leds['red'].turnOn()

        # Check if we let them try again or not
        shouldTryAgain = (self._attemptCount < self._MAX_ATTEMPTS)
        # Inform the Master Server this event failed
        if self.ConnectionManager != None:
            self.ConnectionManager.submitCpaDetectionToMS(hitDetected,False,failMessage)
        # TODO shoud have a final you failed after MAX that is different?
        #self._buzzers['FailBuzzer'].playSynchronously()
        self.playFail()
        self._leds['red'].turnOff()
        if shouldTryAgain:
          # signal to do over
          # TODO do we want some kind of special state to show restart?
          # Have the green lights go in reverse back to the start at minimum
          resetStepInSeconds = 3.0 / 15.0 # TODO change 3 to theatric delay
          for i in range(15, -1, -1):
            #fade is taking too much cpu with 16 threads so keeping in one loop
            #self._leds[str(i)].fade(100,0,resetStepInSeconds*2)
            #time.sleep(resetStepInSeconds)
            self._leds[str(i)].turnOn()
            nextStepTime = time.time() + resetStepInSeconds
            while (time.time() < nextStepTime):
              # Yes we could tighten this loop but leaving as is so overall timing
              # is more consistent to stick with idea of constant velocity
              for j in range(15, -1, -1):
                self._leds[str(j)].decay()
                self._leds[str(j)].decay()
                self._leds[str(j)].decay()
                self._leds[str(j)].decay()
                self._leds[str(j)].decay()
                self._leds[str(j)].decay()
        else:
          # All done so have the main thread go back to waiting state
          self._isRunning = False

        # Even if done for this round need to reset for the next team
        self._isNewStartOrRetry = True

    # --------------------------------------------------------------------------
    def onPassed(self,
                 msg):
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
        logger.info('CPA transitioned to Passed state with msg [%s].' % (msg))

        # Reset inputs and outputs
        self._powerOutputs["LaserWindow"].stop()
        for name in self._leds.keys():
            self._leds[name].turnOff()
        for name in self._buzzers.keys():
            self._buzzers[name].off()
        self._leds['green'].turnOn()

        # Inform the Master Server this event passed
        if self.ConnectionManager != None:
            self.ConnectionManager.submitCpaDetectionToMS('True','True',msg)

        #self._buzzers['SuccessBuzzer'].playSynchronously()
        try:
          self.playBond()
        except Exception, e:
          exType, ex, tb = sys.exc_info()
          logger.critical("Exception occurred of type %s in cpa playing bond: %s" % (exType.__name__, str(e)))
          traceback.print_tb(tb)
          
        #time.sleep(10)
        self._leds['green'].turnOff()
        # All done so have the main thread go back to waiting state
        self._isRunning = False
        # And reset for the next team
        self._isNewStartOrRetry = True

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

