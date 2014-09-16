from abc import ABCMeta, abstractmethod
import logging
import logging.handlers


# ------------------------------------------------------------------------------
class ILed:
   __metaclass__ = ABCMeta

   # ---------------------------------------------------------------------------
   @abstractmethod
   def turnOff(self):
      pass

   # ---------------------------------------------------------------------------
   @abstractmethod
   def turnOn(self):
      pass

   # ---------------------------------------------------------------------------
   @abstractmethod
   def setFlashing(self):
      pass


#TODO Delete dead code, clean up imports
## ------------------------------------------------------------------------------
#class IPushButton:
#   __metaclass__ = ABCMeta
#
#   # ---------------------------------------------------------------------------
#   @abstractmethod
#   def run(self):
#      pass
#
#   # ---------------------------------------------------------------------------
#   @abstractmethod
#   def startListening(self):
#      pass
#
#   # ---------------------------------------------------------------------------
#   @abstractmethod
#   def stopListening(self):
#      pass


# ------------------------------------------------------------------------------
class IVibrationMotor:
   __metaclass__ = ABCMeta

   # ---------------------------------------------------------------------------
   @abstractmethod
   def start(self):
      pass

   # ---------------------------------------------------------------------------
   @abstractmethod
   def stop(self):
      pass


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

