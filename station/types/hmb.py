import logging
import logging.handlers
from station.interfaces import IStation
import sys
from threading import Thread
import time
import traceback
from time import sleep
from time import time


# ------------------------------------------------------------------------------
class Station(IStation):

    # --------------------------------------------------------------------------
    def __init__(self,
                 config,
                 hwModule):
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
        logger.info('Starting HMB.')

        # Nothing more to do.

    # --------------------------------------------------------------------------
    def stop(self, signal):
        logger.info('Received signal "%s". Stopping HMB.', signal)

        for motor in self._vibrationMotors:
            motor.stop()

    # --------------------------------------------------------------------------
    def onReady(self):
        logger.info('HMB transitioned to Ready state.')

        for motor in self._vibrationMotors:
            motor.stop()

        for name in self._leds.keys():
            self._leds[name].turnOff()

    # --------------------------------------------------------------------------
    def onProcessing(self):
        logger.info('HMB transitioned to Processing state.')

        for motor in self._vibrationMotors:
            motor.start()

        for name in self._leds.keys():
            self._leds[name].turnOff()

        self._leds['yellow'].turnOn()

    # --------------------------------------------------------------------------
    def onFailed(self):
        logger.info('HMB transitioned to Failed state.')

        for motor in self._vibrationMotors:
            motor.stop()

        for name in self._leds.keys():
            self._leds[name].turnOff()

        self._leds['red'].turnOn()

    # --------------------------------------------------------------------------
    def onPassed(self):
        logger.info('HMB transitioned to Passed state.')

        for motor in self._vibrationMotors:
            motor.stop()

        for name in self._leds.keys():
            self._leds[name].turnOff()

        self._leds['green'].turnOn()

    # --------------------------------------------------------------------------
    def onUnexpectedState(self, value):
        logger.critical('HMB transitioned to Unexpected state %s', value)

        for name in self._leds.keys():
            self._leds[name].setFlashing()


# ------------------------------------------------------------------------------
class VibrationManager:

    # --------------------------------------------------------------------------
    def __init__(self,
                 name,
                 config,
                 vibrationMotorClass):
        self.Name = name
        logger.debug('Constructing vibration manager %s', self.Name)
        self._timeToExit = False
        self.OnDuration_s = config.OnDuration_s
        self.OffDuration_s = config.OffDuration_s
        self._vibrationMotor = vibrationMotorClass(self.Name)

        self._currentlyStarted = False
        self._transitionToStarted = False

        self._thread = Thread(target = self.run)
        self._thread.daemon = True
        self._thread.start()

    # --------------------------------------------------------------------------
    def __enter__(self):
        logger.debug('Entering vibration manager %s', self.Name)
        return self

    # --------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        logger.debug('Exiting vibration manager %s', self.Name)
        stopListening(self)
        self._timeToExit = True
        self._thread.join()

    # --------------------------------------------------------------------------
    def run(self):
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
                        configDuration_s = self.OffDuration_s
                        motorToggle = self._vibrationMotor.stop
                    else:
                        configDuration_s = self.OnDuration_s
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
    def start(self):
        logger.debug('Starting vibration manager %s', self.Name)
        self._transitionToStarted = True

    # --------------------------------------------------------------------------
    def stop(self):
        logger.debug('Stopping vibration manager %s', self.Name)
        self._transitionToStarted = False


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

