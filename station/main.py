from importlib import import_module
import logging
import logging.handlers
from station.state import State
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
      self._state = None

   # ---------------------------------------------------------------------------
   def start(self):
      logger.info('Starting StationLoader.')

      self.State = State.READY
      self._station.start()
      self._connectionManager.startListening()

      while True:
         sleep(1)

   # ---------------------------------------------------------------------------
   def stop(self, signal):
      logger.info('Received signal "%s". Stopping StationLoader.', signal)

      self._station.stop(signal)
      self._connectionManager.stopListening()

   # ---------------------------------------------------------------------------
   @property
   def State(self):
      return self._state

   @State.setter
   def State(self, value):
      logger.debug('State transition from %s to %s' % (self._state, value))
      self._state = value

      if value == State.READY:
         self._station.onReady()
      elif value == State.PROCESSING:
         self._station.onProcessing()
      elif value == State.FAILED:
         self._station.onFailed()
      elif value == State.PASSED:
         self._station.onPassed()
      else:
         self._station.onUnexpectedState(value)

   @State.deleter
   def State(self):
      del self._state


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

