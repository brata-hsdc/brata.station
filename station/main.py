import logging
import logging.handlers
# TODO Run pylint
from hmb import Hmb # TODO Delete


# ------------------------------------------------------------------------------
class StationLoader(object):

   # ---------------------------------------------------------------------------
   def __init__(self,
                config):
      logger.debug('Constructing StationLoader')

      self._station = Hmb(config)

   # ---------------------------------------------------------------------------
   def start(self):

      logger.info('Starting StationLoader.')
      self._station.start()

   # ---------------------------------------------------------------------------
   def stop(self, signal):

      logger.info('Received signal "%s". Stopping StationLoader.', signal)
      self._station.stop(signal)


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

