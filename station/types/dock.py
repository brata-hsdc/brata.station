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
from __future__ import print_function, division

#import operator
#import logging
import logging.handlers
#import time
from multiprocessing import Process, Queue
from collections import namedtuple

from station.interfaces import IStation
from flight_profile.FlightProfile import FlightProfileApp
from flight_profile.DockSim import FlightParams


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
        self.ConnectionManager = None

        self._flightSim = FlightProfileApp()
        self._flightSim.fullscreen = True
        self._flightSim.stationCallbackObj = None
        
        self._simProcess = None  # sim graphics will run as a separate process
        self._simQueue   = None  # main process will pass data to sim process through this queue

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

        # Spawn sim process
        logger.info("ConnectionManager._callback is {}".format(repr(self.ConnectionManager._callback)))
        self._flightSim.stationCallbackObj = self.ConnectionManager._callback

        if self._simQueue is None:
            self._simQueue = Queue()
            self._simProcess = Process(target=self._flightSim.runFromQueue, args=(self._simQueue,))
            self._simProcess.start()

    # --------------------------------------------------------------------------
    def stop(self, signal):
        """ Stop the station Dock application """
        logger.info('Received signal "%s". Stopping DOCK.', signal)

        # Shutdown sim process
        if self._simQueue:
            self._simQueue.put((FlightProfileApp.QUIT_CMD, ""))
            self._simProcess.join()
            self._simProcess = None
            self._simQueue = None

    # --------------------------------------------------------------------------
    def onReady(self):
        """ Put the application in its initial starting state """
        logger.info('DOCK transitioned to Ready state.')
        if self._simQueue:
            self._simQueue.put((FlightProfileApp.READY_CMD, ""))

    # --------------------------------------------------------------------------
    def onProcessing(self, args):
        """ Accept parameters to run the dock simulation, and start the sim. """
        logger.info('DOCK transitioned to Processing state with args {}.'.format(repr(args)))
        if self._simQueue:
            self._simQueue.put((FlightProfileApp.WELCOME_CMD, args))

    # --------------------------------------------------------------------------
    def onProcessing2(self, args):
        """Transition station to the Processing2 state

        Args:
            a namedtuple containing all the flight parameters
            TODO: list the flight parameters
        """
        logger.info('DOCK transitioned to Processing2 state.' )

        if self._simQueue:
            flightProfile = FlightParams(tAft=float(args.t_aft),
                                         tCoast=float(args.t_coast),
                                         tFore=float(args.t_fore),
                                         aAft=float(args.a_aft),
                                         aFore=float(args.a_fore),
                                         rFuel=float(args.r_fuel),
                                         qFuel=float(args.q_fuel),
                                         dist=float(args.dist),
                                         vMin=float(args.v_min),
                                         vMax=float(args.v_max),
                                         vInit=float(args.v_init),
                                         tSim=int(args.t_sim),
                                        )
            self._simQueue.put((FlightProfileApp.RUN_CMD, flightProfile))
     
    # --------------------------------------------------------------------------
    def onProcessingCompleted(self, args):
        """Transition station to the ProcessingCompleted state
 
        This state will be entered when the graphics thread sets the state
        to ProcessingCompleted.
         
        Args:
            isCorrect
            elapsedTimeSec
            failMsg
        """
        logger.info('DOCK transitioned to ProcessingCompleted state.' )
        logger.info('TODO implement method body.' )
        isCorrect,elapsedTimeSec,failMsg = args
        logger.info('Submitting isCorrect: {} , simTimeSec: {}, failMsg: {}'.format(isCorrect, elapsedTimeSec, failMsg))
        self.ConnectionManager.submit(candidateAnswer=elapsedTimeSec,
                                      isCorrect=isCorrect,
                                      failMessage=failMsg)

    # --------------------------------------------------------------------------
    def onFailed(self,
                 args):
        """TODO strictly one-line summary
        """
        logger.info('DOCK transitioned to Failed state with args [%s].' % (args))
        theatric_delay, is_correct, challenge_complete = args

    # --------------------------------------------------------------------------
    def onPassed(self,
                 args):
        """TODO strictly one-line summary
        """
        logger.info('DOCK transitioned to Passed state with args [%s].' % (args))

    # --------------------------------------------------------------------------
    def onUnexpectedState(self, value):
        """TODO strictly one-line summary
        """
        logger.critical('DOCK transitioned to Unexpected state %s', value)

# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

