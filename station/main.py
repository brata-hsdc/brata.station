# ------------------------------------------------------------------------------
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ------------------------------------------------------------------------------
"""
The main entry point for the station application.
"""

from importlib import import_module
import logging
import logging.handlers
from time import sleep

from station.state import State


# ------------------------------------------------------------------------------
class StationLoader(object):
    """
    Manages a specific station type based on the application configuration.
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 config):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            arg2 (type2): TODO describe arg, valid values, etc.
            arg3 (type3): TODO describe arg, valid values, etc.
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        logger.debug('Constructing StationLoader')

        connectionModuleName = config.ConnectionModuleName
        hwModuleName = config.HardwareModuleName
        connectionManagerClassName = config.ConnectionManagerClassName
        stationModuleName = config.StationType
        stationClassName = config.StationClassName

        connectionModule = import_module(connectionModuleName)
        hwModule = import_module(hwModuleName)
        stationModule = import_module(stationModuleName)

        connectionManagerClass = getattr(connectionModule,
                                         connectionManagerClassName)
        stationClass = getattr(stationModule, stationClassName)

        self._station = stationClass(config.StationTypeConfig, hwModule)
        logger.debug('Constructed station of type %s' % (self._station.stationTypeId))
        self._connectionManager = connectionManagerClass(
                                     self,
                                     self._station.stationTypeId,
                                     config.ConnectionManager)

        self._station.ConnectionManager = self._connectionManager
        self._state = None
        self.args = None

    # --------------------------------------------------------------------------
    def start(self):
        """Starts the station instance.

        Starts the station instance in the Ready state, initiates a connection
        with the MS, and begins listening for messages from the MS.

        Args:
            N/A.
        Returns:
            N/A.
        Raises:
            N/A.

        """
        logger.info('Starting StationLoader.')

        self.State = State.READY
        self._station.start()
        self._connectionManager.startListening()

        while True:
            sleep(1)

    # --------------------------------------------------------------------------
    def stop(self, signal):
        """Stops the station instance.

        Stops the station instance and stops listening to messages from the MS.

        Args:
            signal (int): The number of the signal being handled.
            N/A.
        Returns:
            N/A.
        Raises:
            N/A.

        """
        logger.info('Received signal "%s". Stopping StationLoader.', signal)

        self._station.stop(signal)
        self._connectionManager.stopListening()
        # TODO maybe stop connection manager before stopping station?

    # --------------------------------------------------------------------------
    @property
    def State(self):
        """The current station state.

        Indicates whether the station is ready to run a challenge, running a
        challenge, or completed a challenge with a passed or failed result.

        Args:
            N/A.
        Returns:
            The current station state.
        Raises:
            N/A.

        """
        return self._state

    @State.setter
    def State(self, value):
        logger.debug('State transition from %s to %s with args [%s]' % (self._state, value, self.args))
        self._state = value

        if value == State.READY:
            self._station.onReady()
        elif value == State.PROCESSING:
            self._station.onProcessing(self.args)
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

