import logging
import logging.handlers


# ------------------------------------------------------------------------------
class Led(ILed):

   # ---------------------------------------------------------------------------
   def __init__(self,
                name):
      self.Name = name
      self.FlashingOnDuration_s = 0.5
      self.FlashingOffDuration_s = 0.5

   # ---------------------------------------------------------------------------
   def turnOn(self):
      logger.debug('Set LED steady ON \"%s\".', self.Name)
      # TODO

   # ---------------------------------------------------------------------------
   def turnOff(self):
      logger.debug('Set LED steady OFF \"%s\".', self.Name)
      # TODO

   # ---------------------------------------------------------------------------
   def setFlashing(self):
      logger.debug('Set LED flashing \"%s (%s..%s)\".',
                   self.Name,
                   self.FlashingOnDuration_s,
                   self.FlashingOffDuration_s)
      # TODO
      pass


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
#                  # TODO
#                  pass
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
#      # TODO
#      self._listening = True
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
      # TODO

   # ---------------------------------------------------------------------------
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

