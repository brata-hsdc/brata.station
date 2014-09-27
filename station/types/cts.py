import logging
import logging.handlers
from station.interfaces import IStation


# ------------------------------------------------------------------------------
class Station(IStation):

   # ---------------------------------------------------------------------------
   def __init__(self,
                config,
                hwModule):
      logger.debug('Constructing CTS')

      # TODO - add code here

   # ---------------------------------------------------------------------------
   def start(self):
      logger.info('Starting CTS.')

      # TODO - add code here

   # ---------------------------------------------------------------------------
   def stop(self, signal):
      logger.info('Received signal "%s". Stopping CTS.', signal)

      # TODO - add code here

   # ---------------------------------------------------------------------------
   def onReady(self):
      logger.info('CTS transitioned to Ready state.')

      # TODO - add code here

   # ---------------------------------------------------------------------------
   def onProcessing(self):
      logger.info('CTS transitioned to Processing state.')

      # TODO - add code here

   # ---------------------------------------------------------------------------
   def onFailed(self):
      logger.info('CTS transitioned to Failed state.')

      # TODO - add code here

   # ---------------------------------------------------------------------------
   def onPassed(self):
      logger.info('CTS transitioned to Passed state.')

      # TODO - add code here

   # ---------------------------------------------------------------------------
   def onUnexpectedState(self, value):
      logger.critical('CTS transitioned to Unexpected state %s', value)

      # TODO - add code here


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

