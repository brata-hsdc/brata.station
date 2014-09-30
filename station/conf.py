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
TODO module description
"""

import logging
import logging.handlers


# ------------------------------------------------------------------------------
class StationLoaderConfig:
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self):
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
        logger.debug('Constructing Station config')

        #---
        # Enable one of the following for the connection. TODO Blah blah blah.
        #---
        #self.ConnectionModuleName = 'station.console' # TODO Unimplemented
        self.ConnectionModuleName = 'station.connection'


        self.ConnectionManagerClassName = 'ConnectionManager'
        self.ConnectionManager = ConnectionManagerConfig()


        #---
        # Enable one of the following for the hardware. The console module
        # simulates the hardware using console functions. This means the LEDs and
        # vibration motor status will be printed to the logs instead of really
        # lighting up or vibrating.
        #---
        self.HardwareModuleName = 'station.console'
        #self.HardwareModuleName = 'station.hw'


        #---
        # Enable one of the following modules to select the station type. The
        # module is expected to define a class named the value of
        # StationClassName. This is the starting point for a station.
        #---
        self.StationType = 'station.types.hmb'
        #self.StationType = 'station.types.cpa'
        #self.StationType = 'station.types.cts'


        self.StationClassName = 'Station'
        self.StationTypeConfig = StationTypeConfig()


# ------------------------------------------------------------------------------
class StationTypeConfig:
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self):
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
        logger.debug('Constructing Station type config')

        self.LedClassName = 'Led'
        self.VibrationMotorClassName = 'VibrationMotor'

        # period = 1.0 sec
        # want motor 1 to be on 1/5 of the time, off remainder
        # want motor 2 to be on 1/7 of the time, off remainder
        # want motor 3 to be on 1/11 of the time, off remainder
        # (note the inverse of prime numbers)

        self.VibrationMotors = [
           #                    name     on (s)      off (s)
           #                    -----    ----------  -----------
           VibrationMotorConfig('Huey',  1.0 /  5.0,  4.0 /  5.0),
           VibrationMotorConfig('Dewey', 1.0 /  7.0,  6.0 /  7.0),
           VibrationMotorConfig('Louie', 1.0 / 11.0, 10.0 / 11.0),
        ]

        self.Leds = [
           LedConfig('red'   ),
           LedConfig('yellow'),
           LedConfig('green' )
        ]


# ------------------------------------------------------------------------------
class LedConfig:
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 name):
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
        self.Name = name
        logger.debug('Constructing LED %s config', self.Name)


# ------------------------------------------------------------------------------
class VibrationMotorConfig:
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 name,
                 onDuration_s,
                 offDuration_s):
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
        self.Name = name
        logger.debug('Constructing vibration motor %s config', self.Name)
        self.OnDuration_s = onDuration_s
        self.OffDuration_s = offDuration_s

# ------------------------------------------------------------------------------
class ConnectionManagerConfig:
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self):
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
        logger.debug('Constructing Connection Manager config')
        self.StationInstanceId = '01'
        self.StationType = 'HMB'

        self.ConnectUrl = 'http://localhost:8080/ms/1.0.0/connect';
        self.DisconnectUrl = 'http://localhost:8080/ms/1.0.0/disconnect';
        self.TimeExpiredUrl = 'http://localhost:8080/ms/1.0.0/time_expired';


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

