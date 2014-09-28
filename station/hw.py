from interfaces import ILed
from interfaces import IVibrationMotor
import logging
import logging.handlers


# ------------------------------------------------------------------------------
class Led(ILed):

    # --------------------------------------------------------------------------
    def __init__(self,
                 name):
        self.Name = name
        self.FlashingOnDuration_s = 0.5
        self.FlashingOffDuration_s = 0.5

    # --------------------------------------------------------------------------
    def turnOn(self):
        logger.debug('Set LED steady ON \"%s\".', self.Name)
        # TODO

    # --------------------------------------------------------------------------
    def turnOff(self):
        logger.debug('Set LED steady OFF \"%s\".', self.Name)
        # TODO

    # --------------------------------------------------------------------------
    def setFlashing(self):
        logger.debug('Set LED flashing \"%s (%s..%s)\".',
                     self.Name,
                     self.FlashingOnDuration_s,
                     self.FlashingOffDuration_s)
        # TODO
        pass


# ------------------------------------------------------------------------------
class VibrationMotor(IVibrationMotor):

    # --------------------------------------------------------------------------
    def __init__(self,
                 name):
        self.Name = name

    # --------------------------------------------------------------------------
    def __enter__(self):
        logger.debug('Entering vibration motor %s', self.Name)
        return self

    # --------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        logger.debug('Exiting vibration motor %s', self.Name)
        stop(self)

    # --------------------------------------------------------------------------
    def start(self):
        logger.debug('Started vibration motor \"%s\".', self.Name)
        # TODO

    # --------------------------------------------------------------------------
    def stop(self):
        logger.debug('Stopped vibration motor \"%s\".', self.Name)
        # TODO


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

