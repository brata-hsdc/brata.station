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
Provides the definitions needed for the Dock station type.
"""

import operator
import logging
import logging.handlers
import time

from station.interfaces import IStation
from flight_profile.FlightProfile import FlightProfileApp


# ------------------------------------------------------------------------------
class Station(IStation):
    """
    Provides the implementation for a Dock station to drive the graphical
    docking simulation display.
    """
    
    # --------------------------------------------------------------------------
    def __init__(self,
                 config,
                 hwModule):
        """ Initialize the graphical display and the simulation engine

        The Dock simulation uses pygame to drive the display.

        Args:
            config:    a Config object containing properties to configure station characteristics
            hwModule:  python module object that defines hardware interfaces
        """
        logger.debug('Constructing DOCK')

##        displayClassName = config.DisplayClassName
##        pushButtonMonitorClassName = config.PushButtonMonitorClassName
##
##        displayClass = getattr(hwModule, displayClassName)
##        pushButtonMonitorClass = getattr(hwModule, pushButtonMonitorClassName)
##
##        self._display = displayClass(config.Display)
        
#         self._display.setText("Initializing...")
# 
#         logger.info('Initializing pushButtonMonitor')
#         self._pushButtonMonitor = pushButtonMonitorClass()
#         self._pushButtonMonitor.setDevice(self._display._lcd)
# 
#         for i in config.PushButtons:
#             logger.info('  Setting button {}'.format(i))
#             self._pushButtonMonitor.registerPushButton(i.Name,
#                                                        self.buttonPressed,
#                                                        i)
# 
#         self._centerOffset = 0  # amount of space to left of displayed combination
        self.ConnectionManager = None
        
#         self._combo = None  # will hold a Combo object
#         self._timedMsg = None  # generator
#         self._timedMsgNextState = self.IDLE_STATE
#         self._colorToggle = None  # generator
#         
#         self._preInputDuration   =  6.0  # seconds to display msg
#         self._passedDuration     =  7.5  # seconds to display msg
#         self._failedDuration     =  5.0  # seconds to display msg
#         self._preIdleDuration    =  5.0  # seconds to display msg
#         self._prePassedDuration  =  5.0  # seconds to display msg
#         self._preFailedDuration  =  5.0  # seconds to display msg
#         self._submittedDuration  =  2.0  # seconds to display msg
#         self._sendFinishDuration = 15.0  # seconds to display msg
#         
#         
#         # Background cycle states: ([list of colors], rate_in_sec)
#         # TODO: These constants could be moved to runstation.conf
#         self._preIdleBg    = (["CYAN"], 1.0)
#         self._prePassedBg  = (["YELLOW", "WHITE"], 0.1)
#         self._preFailedBg  = (["YELLOW", "WHITE"], 0.1)
#         self._idleBg       = (["WHITE", "BLUE", "YELLOW", "GREEN", "RED", "CYAN", "MAGENTA"], 0.75)
#         self._preInputBg   = (["YELLOW", "YELLOW", "YELLOW", "YELLOW", "RED"], 0.15)
#         self._inputBg      = (["CYAN"], 1.0)
#         self._submit1Bg    = (["RED", "WHITE"], 0.15)
#         self._submit2Bg    = (["WHITE"], 1.0)
#         self._passedBg     = (["GREEN", "CYAN"], 1.0)
#         #self._failedBg    = (["RED"], 1.0)
#         self._failedBg     = (["RED", "RED", "RED", "RED", "RED", "RED", "RED", "RED", "RED", "WHITE"], 0.1)
#         self._sendFinishBg = (["YELLOW", "YELLOW", "YELLOW", "YELLOW", "RED"], 0.15)
#         self._shutdownBg   = (["BLUE"], 1.0)
#         self._errorBg      = (["RED", "RED", "RED", "RED", "RED", "WHITE"], 0.15)
#         
#         # Display text for different states
#         # TODO: These constants could be moved to runstation.conf
#         self._preIdleText         = "  Resetting...\n"
#         self._prePassedText       = "- Trying Your -\n- Combination -"
#         self._preFailedText       = "- Trying Your -\n- Combination -"
#         self._idleText            = "==== CRACK =====\n== THE = SAFE =="
#         self._preInputText        = "      HEY!!\n  Scan QR Code"
#         self._enterLine1Text      = "Enter Code:"
#         self._submittingLine1Text = "2nd ENTER Sends"
#         self._submittedLine1Text  = "=Code Submitted="
#         self._passedText          = "  The Safe Is\n    UNLOCKED"
#         self._failedText          = "  The Safe Is\n  STILL LOCKED"
#         self._sendFinishText      = "     Submit\n   Your  Data"
#         self._shutdownText        = "Shutting down..."
#         self._errorText           = "  Malfunction!\n"
# 
#         # Station current operating state
#         self._ctsState = self.START_STATE
#         self._pushButtonMonitor.setOnTickCallback(self.onTick)

        self._flightSim = FlightProfileApp()

    # --------------------------------------------------------------------------
    @property
    def stationTypeId(self):
        """ Identifies this station's type as DOCK.

            Returns:
                "DOCK"
        """
        return "DOCK"

    # --------------------------------------------------------------------------
    def start(self):
        """ Start the station Dock application """
        logger.info('Starting DOCK.')

        # Nothing more to do.

    # --------------------------------------------------------------------------
    def stop(self, signal):
        """ Stop the station Dock application """
        logger.info('Received signal "%s". Stopping DOCK.', signal)
#         self.enterState(self.SHUTDOWN_STATE)

    # --------------------------------------------------------------------------
    def onReady(self):
        """ Put the application in its initial starting state """
        logger.info('DOCK transitioned to Ready state.')
#         self.enterState(self.IDLE_STATE)

    # --------------------------------------------------------------------------
    def onProcessing(self, args):
        """ Accept parameters to run the dock simulation, and start the sim. """
        logger.info('DOCK transitioned to Processing state with args [%s].' % (args))

        flightProfile = FlightProfileApp.FlightParams(tAft=args.tAft,
                                                      tCoast=args.tCoast,
                                                      tFore=args.tFore,
                                                      aAft=args.aAft,
                                                      aFore=args.aFore,
                                                      rFuel=args.rFuel,
                                                      qFuel=args.qFuel,
                                                      dist=args.dist,
                                                      vMin=args.vMin,
                                                      vMax=args.vMax,
                                                      vInit=args.vInit,
                                                      tSim=args.tSim,
                                                     )
        self._flightSim.fullscreen = args.fullscreen
        self._flightSim.run(flightProfile)

    # --------------------------------------------------------------------------
    def onFailed(self,
                 args):
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
        logger.info('DOCK transitioned to Failed state with args [%s].' % (args))
        theatric_delay, is_correct, challenge_complete = args
#         if challenge_complete.lower() == "true":
#             self.enterState(self.PRE_FAILED_STATE)
#         else:
#             self.enterState(self.PRE_FAILED_RETRY_STATE)
# 
#         self._pushButtonMonitor.stopListening()

    # --------------------------------------------------------------------------
    def onPassed(self,
                 args):
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
        logger.info('DOCK transitioned to Passed state with args [%s].' % (args))
#         self.enterState(self.PRE_PASSED_STATE)
# 
#         self._pushButtonMonitor.stopListening()

    # --------------------------------------------------------------------------
    def onUnexpectedState(self, value):
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
        logger.critical('DOCK transitioned to Unexpected state %s', value)
#         self.enterState(self.ERROR_STATE)

# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

