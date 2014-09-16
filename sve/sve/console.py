from interfaces import ILed
from interfaces import IVibrationMotor
#TODO Delete from interfaces import ILed, IPushButton, IVibrationMotor
import logging
import logging.handlers
from sve.util import NonBlockingConsole
from threading import Thread
from time import sleep


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


#TODO Delete dead code, clean up imports
## ------------------------------------------------------------------------------
#class PushButton(IPushButton):
#
#   # ---------------------------------------------------------------------------
#   def __init__(self,
#                buttonPressHandler,
#                config):
#      logger.debug('Constructing push button')
#      self._listening = False
#      self._timeToExit = False
#      self._handler = buttonPressHandler
#      self._thread = Thread(target = self.run)
#      self._thread.daemon = True
#      self._thread.start()
#
#   # ---------------------------------------------------------------------------
#   def __enter__(self):
#      logger.debug('Entering push button')
#      return self
#
#   # ---------------------------------------------------------------------------
#   def __exit__(self, type, value, traceback):
#      logger.debug('Exiting push button')
#      stopListening(self)
#      self._timeToExit = True
#      self._thread.join()
#
#   # ---------------------------------------------------------------------------
#   def run(self):
#      with NonBlockingConsole() as nbc:
#         logger.debug('Starting key press thread for push button')
#
#         while not self._timeToExit:
#            try:
#               if self._listening:
#
#                  keypress = nbc.get_data()
#
#                  if keypress == ' ':
#                     logger.debug('Received key press event for <SPACE>')
#                     self._handler()
#
#                  # ignore all other key presses
#                  else:
#                     pass
#
#               sleep(1)
#            except Exception, e:
#               # JIA TODO BEGIN change
#               #logging.critical("Exception occurred: " + e.args[0])
#               # JIA TODO UPDATE change
#               exType, ex, tb = sys.exc_info()
#               logging.critical("Exception occurred of type " + exType.__name__)
#               logging.critical(str(e))
#               traceback.print_tb(tb)
#               # JIA TODO END change
#
#   # ---------------------------------------------------------------------------
#   def startListening(self):
#      logger.debug('Starting listening for push button')
#      print "Press <SPACE> to simulate button press."
#      self._listening = True
#
#
#   # ---------------------------------------------------------------------------
#   def stopListening(self):
#      logger.debug('Stopping listening for push button')
#      self._listening = False


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

