from importlib import import_module
import logging
import logging.handlers
from time import sleep
# TODO Run pylint


# ------------------------------------------------------------------------------
class StationLoader(object):

   # ---------------------------------------------------------------------------
   def __init__(self,
                config):
      logger.debug('Constructing StationLoader')

      connectionModuleName = config.ConnectionModuleName
      connectionManagerClassName = config.ConnectionManagerClassName

      connectionModule = import_module(connectionModuleName)
      connectionManagerClass = getattr(connectionModule,
                                       connectionManagerClassName)

      self._connectionManager = connectionManagerClass(self,
                                                       config.ConnectionManager)

      hwModuleName = config.HardwareModuleName
      hwModule = import_module(hwModuleName)

      stationModuleName = config.StationType
      stationClassName = config.StationClassName

      stationModule = import_module(stationModuleName)
      stationClass = getattr(stationModule, stationClassName)

      self._station = stationClass(config.StationTypeConfig, hwModule)

   # ---------------------------------------------------------------------------
   def start(self):

      logger.info('Starting StationLoader.')
      self._station.start()

      self._connectionManager.startListening()

      while True:
         sleep(1)

   # ---------------------------------------------------------------------------
   def stop(self, signal):

      logger.info('Received signal "%s". Stopping StationLoader.', signal)
      self._station.stop(signal)

      self._connectionManager.stopListening()


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

