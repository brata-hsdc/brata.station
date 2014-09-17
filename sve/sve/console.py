from interfaces import ILed
from interfaces import IVibrationMotor
import logging
import logging.handlers


# ------------------------------------------------------------------------------
class Led(ILed):

   # ---------------------------------------------------------------------------
   def __init__(self,
                name,
                config):
      self.Name = name
      logger.debug('Constructing LED %s', self.Name)

   # ---------------------------------------------------------------------------
   def __enter__(self):
      logger.debug('Entering LED %s', self.Name)
      return self

   # ---------------------------------------------------------------------------
   def __exit__(self, type, value, traceback):
      logger.debug('Exiting LED %s', self.Name)
      turnOff(self)

   # ---------------------------------------------------------------------------
   def turnOff(self):
      logger.debug('Turning off LED %s', self.Name)

   # ---------------------------------------------------------------------------
   def turnOn(self):
      logger.debug('Turning on LED %s', self.Name)

   # ---------------------------------------------------------------------------
   def setFlashing(self):
      logger.debug('Set LED %s flashing', self.Name)


# ------------------------------------------------------------------------------
class VibrationMotor(IVibrationMotor):

   # ---------------------------------------------------------------------------
   def __init__(self,
                name):
      self.Name = name

   # ---------------------------------------------------------------------------
   def __enter__(self):
      logger.debug('Entering vibration motor %s', self.Name)
      return self

   # ---------------------------------------------------------------------------
   def __exit__(self, type, value, traceback):
      logger.debug('Exiting vibration motor %s', self.Name)
      stop(self)

   # ---------------------------------------------------------------------------
   def start(self):
      logger.debug('Started vibration motor \"%s\".', self.Name)

   # ---------------------------------------------------------------------------
   def stop(self):
      logger.debug('Stopped vibration motor \"%s\".', self.Name)


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

