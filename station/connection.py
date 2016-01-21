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

from datetime import datetime
import dbus
import json
import logging
import logging.handlers
import sys
from threading import Thread
from time import sleep
from time import time
import httplib
import traceback

from flask import Flask
from flask import request
from flask import jsonify
import requests
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from station.interfaces import IConnectionManager
from station.state import HttpMethod
from station.state import State
from station.util import get_ip_address

from collections import namedtuple

from pi_serial import PiSerial

# ------------------------------------------------------------------------------
class ConnectionManager(IConnectionManager):
    """
    Station Connection Manager
    """

    _app = Flask(__name__)
    _callback = None


    # --------------------------------------------------------------------------
    def __init__(self,
                 station,
                 stationTypeId,
                 config):
        """Station Connection Manager __init__

        Args:
            station (Station): station class
            stationTypeId (type): ID for station
            config (Config): Configuration parameters
        """

        # TODO?
        """
    def __init__(self,
                 todoHandler,
                 config):
        """

        logger.debug('Constructing connection manager for station type ID %s.' % (stationTypeId))
        logger.debug('Flask debugging? %s' % (self._app.config['DEBUG']))
        logger.debug('Flask testing? %s' % (self._app.config['TESTING']))
        logger.debug('Flask logger? %s' % (self._app.config['LOGGER_NAME']))
        logger.debug('Flask server? %s' % (self._app.config['SERVER_NAME']))

        self._ifName = config.NetInterface  # interface name to check first
        self._ipAddr = self.getIp()  # get IP address of active interface
        self._listenPort = 5000

        self._joinUrl = config.JoinUrl
        self._leaveUrl = config.LeaveUrl
        self._timeExpiredUrl = config.TimeExpiredUrl
        self._submitUrl = config.SubmitUrl
        self._stationType = stationTypeId
        self._stationId = config.StationId
        self._resetPin = config.ResetPIN
        self._shutdownPin = config.ShutdownPIN
        self._reallyShutdown = config.ReallyShutdown
        self._connected = False
        self._listening = False
        self._timeToExit = False

        # _callback is actually an instance of StationLoader.
        # StationLoader is defined in main.py.
        # StationLoader has a member called _station that contains
        # a reference to the Station object (which is a Station
        # object instantiated in main.py from dock.py, secure.py,
        # return.py, etc.).
        #
        # The StationLoader is called _callback here because it
        # is used to callback to methods in the Station object
        # by changing the State property.  Values are passed to
        # the callback by setting the StationLoader.args property
        # prior to changing the state, like this:
        #
        #    stationLdr._callback.args = (cbValue1, cbValue2,)
        #    stationLdr._callback.State = State.PROCESSING
        #
        self._callback = station
        #TODO? self._handler = todoHandler

        # Each HTTP message that will be received by the station
        # needs to have a rule defined for it here.  The rule
        # specifies the URL, the HTTP method (GET, POST), and
        # the method to call to handle the incoming message.
        self._app.add_url_rule(config.ResetUrlRule,
                               'reset',
                               self.reset,
                               methods=['GET'])

        self._app.add_url_rule(config.StartChallengeUrlRule,
                               'start_challenge',
                               self.startChallenge,
                               methods=['POST'])

        self._app.add_url_rule(config.PostChallengeUrlRule,
                               'post_challenge',
                               self.postChallenge,
                               methods=['POST'])

        self._app.add_url_rule(config.ShutdownUrlRule,
                             'shutdown',
                             self.shutdown,
                             methods=['GET'])

        # The ConnectionManager (this class) runs in a separate
        # thread, so it can listen for incoming HTTP requests.
        # The thread will first send a Join request to the
        # MasterServer, then upon a successful Join, will
        # start an HTTPServer to handle the incoming requests.
        self._thread = Thread(target = self.run)
        self._thread.daemon = True
        self._thread.start()  # creates the thread, which calls the target method (self.run)

    # --------------------------------------------------------------------------
    def getIp(self):
        """ Determine the IP address that other hosts can use to communicate with
            this one.  Check the interface self._ifName, "eth0", "wlan0", and return
            the first address found.  If none are found, return "127.0.0.1" (localhost).
            
            Returns an IP address as a string
        """
        ipAddr = "127.0.0.1"
        for interfaceName in (self._ifName, "eth0", "wlan0"):
            try:
                ipAddr = get_ip_address(interfaceName)
                break
            except:
                logger.info("Failed to get IP address from {}".format(interfaceName))
        return ipAddr
    
    # --------------------------------------------------------------------------
    @property
    def _connected(self):
        """ Flag to control part of the listener loop in run() """
        return self._connectedValue

    @_connected.setter
    def _connected(self, value):
        """ Flag to control part of the listener loop in run() """
        self._connectedValue = value
        logger.info('Is connection manager connected? %s' % (value))

    # --------------------------------------------------------------------------
    def __enter__(self):
        """ Allows object to be used in a Python "with" statement

        Returns:
            self
        """
        logger.debug('Entering connection manager')
        return self

    # --------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        """ Allows object to be used in a Python "with" statement

        Stops the listener loop and terminates the listener thread.
        """
        logger.debug('Exiting connection manager')
        self.stopListening()
        self._timeToExit = True
        self._thread.join()

    # --------------------------------------------------------------------------
    def run(self):
        """Loops join requests to the Master Server.

        While the Connection Manager is listening, this will loop join requests
        to establish a connection with the Master Server.

        Args:
            self ConnectionManager: Self reference to this class.
        Returns:
            N/A
        Raises:
            ConnectionError: if connection request to Master Server fails.
            Exception: if unexpected exception occurs.

        """
        logger.info('Starting TODO thread for connection manager')

        sleep_time = 5 #TODO load this from runstation.conf file

        while not self._timeToExit:
            try:
                logger.debug('Loop begin for connection manager')
                if self._listening:

                    if (not self._connected):
                        logger.debug('Not connected. Attempting to join.')
                        self.join()
                        logger.debug('Join successful. Setting _connected.')
                        self._connected = True

                        logger.debug('Starting HTTP server listening on port {}.'.format(self._listenPort))
                        server = HTTPServer(WSGIContainer(self._app))
                        server.listen(self._listenPort)
                        logger.warning('TODO This blocks. Need to look into later. (Issue 4)')
                        IOLoop.instance().start()
                        logger.debug('IOLoop started.')
                    else:
                        logger.debug('Already connected.')

                logger.debug('Connection thread sleeping for {} sec'.format(sleep_time))
                sleep(sleep_time)
            except requests.ConnectionError, e:
                logger.critical(str(e))
                self._connected = False
                # TODO nothing to do - cannot connect because remote end is not up;
                # just wait and try again later
                # TODO configurable sleep time...
                sleep(sleep_time)
            except Exception, e:
                exType, ex, tb = sys.exc_info()
                logger.critical("Exception occurred of type %s: %s" % (exType.__name__, str(e)))
                self._connected = False
                traceback.print_tb(tb)

        self.leave()
        logger.info('Stopping TODO thread for connection manager')

    # --------------------------------------------------------------------------
    def startListening(self):
        """ Set self._listening to True
        
        Causes the connection to go live, join the MS, and listen for incoming
        requests.
        """
        logger.debug('Starting listening for connection manager')
        self._listening = True

    # --------------------------------------------------------------------------
    def stopListening(self):
        """ Set self._listening and self._connected to False

        Stops the connection from listening and handling incoming requests.
        """
        logger.debug('Stopping listening for connection manager')
        self._listening = False
        self._connected = False


    # --------------------------------------------------------------------------
    def timestamp(self):
        """ Format the current time and return it as a string.
        
        Returns:
            The current time as a string of the form "YYYY-MM-DD HH:MM:SS"
        """
        ts = time()
        st = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        return st


    # --------------------------------------------------------------------------
    def callService(self,
                    httpMethod,
                    endpointUrl,
                    args):
        """ Send an HTTP message to a remote host and receive the response.

        Send a message using HTTP to a remote host.  The transaction type (GET, POST, etc.)
        is specified by httpMethod.  The message body is assumed to be JSON, and the
        response is also assumed to be JSON.

        Args:
            httpMethod   (str): the transaction type (HttpMethod.GET, HttpMethod.POST, ...)
            endpointnUrl (str): the message destination URL (http://server:port)
            args        (dict): the named fields for the msg body
        Returns:
            (response_status, response_data) where response_status is the status code (200, 404, ...)
            and response data is a JSON object.
        """
        # TODO check if args present - might be null/empty
        #args['message_timestamp'] = self.timestamp()
        logger.debug('Calling service with HTTP method %s, endpoint URL %s, and args %s' % (httpMethod, endpointUrl, args))
        headers = { 'Content-type': 'application/json', "Accept" : "application/json" }
        data = json.dumps(args)
        response = requests.post(endpointUrl, data=data, headers=headers)

#         logger.debug('Service returned %s with for HTTP method %s, endpoint URL %s, and args %s with headers %s, response %s, JSON response %s, and message %s' % (response.status_code, httpMethod, endpointUrl, args, response.headers, response, response.json, json.dumps(response.json)))
        logger.debug('Service returned %s with for HTTP method %s, endpoint URL %s, and args %s with headers %s, response %s, JSON response %s' % (response.status_code, httpMethod, endpointUrl, args, response.headers, response, response.json))
        #logger.debug('Force json %s' % (json.dumps(response.data)))
        
        try:
            retData = response.json()
            logger.debug('json() worked')
            return (response.status_code, retData)
        except:
            logger.debug('json() failed')
        try:
            return (response.status_code, response.json)
        except:
            logger.debug('json failed')
        return (response.status_code, 'None')


    # ===
    # Messages from Station to MS
    # ===
    # --------------------------------------------------------------------------
    def join(self):
        """ Send the station JOIN msg to the MS.
        
        Send the station JOIN msg to the MS to tell the MS that the station has
        come online.  This message provides identifying information to the MS,
        and also provides the address (in URL form) of this station, so the
        MS can send messages to it.
        """
        logger.debug('Station requesting join with master server')

#         url = self._joinUrl + "/" + self._stationId
        url = self._joinUrl
        stationUrl = 'http://%s:%s/rpi' % (self._ipAddr, self._listenPort)

        (status, response) = self.callService(
            HttpMethod.POST, url,
            {
                'station_id'     : self._stationId,
                'station_type'   : self._stationType,
                'station_serial' : PiSerial.serialNumber(),
                'station_url'    : stationUrl,
            })

        if status in (httplib.OK, httplib.ACCEPTED):
            logger.debug('Service %s returned OK' % (url))
        elif status == httplib.BAD_REQUEST:
            logger.critical('Service %s returned BAD_REQUEST' % (url))
        elif status == httplib.NOT_FOUND:
            logger.critical('Service %s returned NOT_FOUND' % (url))
        else:
            logger.critical('Unexpected HTTP status %s received from service %s' % (status, url))


    # --------------------------------------------------------------------------
    def leave(self):
        """ Send the station LEAVE msg to the MS.

        Send the station LEAVE message to the MS to tell the MS that the station
        is going offline.  If this could be done reliably, there would be no
        need for a heartbeat message.
        """
        logger.debug('Station requesting leave from master server')
        url = "{}".format(self._leaveUrl)
        (status, response) = self.callService(HttpMethod.POST, url,
                                             {
                                                'station_id' : self._stationId,
                                             })

        if status == httplib.OK:
            logger.debug('Service %s returned OK' % (url))
        elif status == httplib.NOT_FOUND:
            logger.critical('Service %s returned NOT_FOUND' % (url))
        else:
            logger.critical('Unexpected HTTP response %s received from service %s' % (status, url))


    # --------------------------------------------------------------------------
    def timeExpired(self):
        """ Send time_expired message to MasterServer """
        logger.debug('Station informing master server that time for challenge has expired')

        theatric_delay_ms = 0
        candidate_answer = 0

        url = "{}".format(self._timeExpiredUrl)
        (status, response) = self.callService(HttpMethod.POST, url,
                                              {
                                                'station_id' : self._stationId,
                                              })

        if status == httplib.OK:
            logger.debug('Service %s returned OK' % (url))
        else:
            logger.critical('Unexpected HTTP response %s received from service %s' % (status, url))

        self._callback.args = [theatric_delay_ms, candidate_answer]
        self._callback.State = State.FAILED

    # --------------------------------------------------------------------------
    def submit(self,
                           candidateAnswer,
                           isCorrect, failMessage):
        """ Submit candidate answer to Master Server

        Args:
            candidateAnswer (list): list of 4 values 0-7 for SECURE,
                                    list of 6 values 00-99 for RETURN
            isCorrect (string): "True" or "False"
            failMessage (string): For SECURE, "True" if isCorrect, else
                                  a message indicating failure
        """
        logger.debug('Station submitting answer to master server, Answer=%s, isCorrect=%s, failMessage=%s' % (candidateAnswer, isCorrect, failMessage))
        
        url = self._submitUrl
        (status, response) = self.callService(
            HttpMethod.POST, url,
            {
                'station_id'        : self._stationId,
                'message_version'   : 0,
                'message_timestamp' : self.timestamp(),
                'candidate_answer'  : candidateAnswer,
                'is_correct'        : isCorrect,
                'fail_message'      : "" if str(isCorrect).lower() == "true" else failMessage
            })

        if status == httplib.OK:
            logger.debug('Service %s returned OK' % (url))
            # Note: the str() casts normalize string and bool inputs, but return a str
            self.handleSubmissionResp(str(isCorrect),
                                      str(response['challenge_complete']))
        elif status == httplib.NOT_FOUND:
            logger.critical('Service %s returned NOT_FOUND' % (url))
        else:
            logger.critical('Unexpected HTTP response %s received from service %s' % (status, url))

        logger.debug('SUBMIT')
        logger.debug('Submit response: %s' % (response['challenge_complete']))
        return response['challenge_complete']


    # ===
    # Messages from MS to Station
    # ===
    # --------------------------------------------------------------------------
    def reset(self,
              pin):
        """Transitions the station to the Ready state.

        Transitions the station to the Ready state if the correct PIN is
        provided; otherwise, the reset request is ignored.

        Args:
            pin (int): This must be 31415 in order to reset the station.
        Returns:
            Empty JSON response with OK status code on success.
        """

        logger.debug('Received reset message from MS with json %s' % (json.dumps(request.json)))
        resp = jsonify()

        if pin == self._resetPin:
            logger.debug('Master server successfully requesting station reset with pin "%s"' % (pin))
            self._callback.State = State.READY
            resp.status_code = httplib.OK
        else:
            logger.warning('Master server requesting station reset with invalid pin "%s"' % (pin))
            resp.status_code = httplib.BAD_REQUEST

        return resp


    # --------------------------------------------------------------------------
    def startChallenge(self):
        """ Receive a start_challenge message from the MS

        Changes the station state to onProcessing

        Returns:
            An HTTP response with the response code set, and an empty JSON body
        """
        logger.debug('Received startChallenge message from MS with json %s' % (json.dumps(request.json)))

        # TODO...
        #if not request.json or not 'title' in request.json:
        if not request.json:
            #TODO abort(httplib.BAD_REQUEST
            logger.debug('return BAD_REQUEST?')

        message_version   = request.json['message_version'] if 'message_version' in request.json else ""
        message_timestamp = request.json['message_timestamp'] if 'message_timestamp' in request.json else ""
        theatric_delay_ms = request.json['theatric_delay_ms'] if 'theatric_delay_ms' in request.json else ""

        if 'secure_tone_Pattern' in request.json:
            logger.debug('Received a start_challenge request for SECURE station')
            secure_tone_pattern = request.json['secure_tone_Pattern']
            secure_state = request.json['secure_state']
            self._callback.args = [secure_tone_pattern] # The Pulse pattern is not required, since it is in the tone pattern
            logger.debug('Master server requesting station start_challenge (ver %s) at %s, SECURE Tone pattern %s, SECURE State %s' % (message_version, message_timestamp, secure_tone_pattern, secure_state))
        elif 'return_guidance_pattern' in request.json:
            logger.debug('Received a start_challenge request for RETURN station')
            return_guidance_pattern = request.json['return_guidance_Pattern']
            self._callback.args = return_guidance_pattern
            logger.debug('Master server requesting station start_challenge (ver %s) at %s, RETURN Guidance pattern %s' % (message_version, message_timestamp, return_guidance_pattern))
        elif 'team_name' in request.json:
            logger.debug('Received a start_challenge request for DOCK station')
#             Args = namedtuple("Args", "t_aft, t_coast, t_fore, a_aft, a_fore, r_fuel, q_fuel, dist, v_min, v_max, v_init, t_sim")
#             args = Args._make([request.json[f] for f in Args._fields])
            self._callback.args = (request.json["team_name"],)
            logger.debug('Master server requesting station start_challenge with args: ' + repr(self._callback.args))
        else:
            logger.critical('Received a start_challenge request for unrecognized station')

        # TODO...

        # TODO implement method body
        self._callback.State = State.PROCESSING

        # TODO can't pass-in self - how to get handle to self? is it needed?

        # TODO
        resp = jsonify({})
        resp.status_code = httplib.OK
        return resp

    # --------------------------------------------------------------------------
    def postChallenge(self):
        """Start the second part of the challenge 

        Returns:
            An HTTP response with an empty JSON body
        """

        logger.debug('Received POST message from MS with json %s' % (json.dumps(request.json)))

        if not request.json:
            #TODO abort(httplib.BAD_REQUEST
            logger.debug('return BAD_REQUEST?')

        message_version = request.json['message_version'] if "message_version" in request.json else ""
        message_timestamp = request.json['message_timestamp'] if "message_timestamp" in request.json else ""

        if 'secure_pulse_Pattern' in request.json:
            logger.debug('Received a post_challenge request for SECURE station')
            secure_pulse_pattern = request.json['secure_pulse_Pattern']
            secure_max_pulse_width = request.json['secure_max_pulse_width']
            secure_max_gap = request.json['secure_max_gap']
            secure_min_gap = request.json['secure_min_gap']

            self._callback.args = [secure_pulse_pattern, secure_max_pulse_width, secure_max_gap, secure_min_gap] # The Pulse pattern is not required, since it is in the tone pattern
            logger.debug('Master server requesting station post_challenge (ver %s) at %s, SECURE Code pattern %s, Max pulse width %s, Max pulse gap %s, Min pulse gap %s' % (message_version, message_timestamp, secure_pulse_pattern, secure_max_pulse_width, secure_max_gap, secure_min_gap))
        elif 't_aft' in request.json:
            logger.debug('Received a post_challenge request for DOCK station')
            Args = namedtuple("Args", "t_aft, t_coast, t_fore, a_aft, a_fore, r_fuel, q_fuel, dist, v_min, v_max, v_init, t_sim")
            args = Args._make([request.json[f] for f in Args._fields])
            self._callback.args = args
            logger.debug('Master server requesting station start_challenge with args: ' + repr(self._callback.args))
        else:
            logger.critical('Received a post_challenge request for unrecognized station')

        self._callback.State = State.PROCESSING2

        resp = jsonify({})
        resp.status_code = httplib.OK
        return resp

##    # --------------------------------------------------------------------------
######### Leaving this in for now for reference
##    def handleSubmission(self):
##        """TODO strictly one-line summary
##
##        TODO Detailed multi-line description if
##        necessary.
##
##        Args:
##            arg1 (type1): TODO describe arg, valid values, etc.
##            arg2 (type2): TODO describe arg, valid values, etc.
##            arg3 (type3): TODO describe arg, valid values, etc.
##        Returns:
##            TODO describe the return type and details
##        Raises:
##            TodoError1: if TODO.
##            TodoError2: if TODO.
##
##        """
##
##        logger.debug('Received handleSubmission message from MS with json %s' % (json.dumps(request.json)))
##
##        # TODO...
##        #if not request.json or not 'title' in request.json:
##        if not request.json:
##            #TODO abort(httplib.BAD_REQUEST
##            logger.debug('return BAD_REQUEST?')
##
##        message_version = request.json['message_version']
##        message_timestamp = request.json['message_timestamp']
##        theatric_delay_ms = request.json['theatric_delay_ms']
##        is_correct = str(request.json['is_correct'])
##        challenge_complete = str(request.json['challenge_complete'])
##
##        logger.debug('Master server relaying (ver %s) user answer to at %s. Theatric delay %s ms is correct? %s. Challenge complete? %s' % (message_version, message_timestamp, theatric_delay_ms, is_correct, challenge_complete))
##        self.handleSubmissionResp(str(is_correct),
##                                  str(challenge_complete))
##
##        resp = jsonify({})
##        resp.status_code = httplib.OK
##        return resp


    # --------------------------------------------------------------------------
    def handleSubmissionResp(self,
                             is_correct,
                             challenge_complete):
        """ This is called when the response comes back after sending a Submit to the MS

        This causes the station state to transition to either PASSED or FAILED, which
        will result in the station's onPassed() or onFailed() method getting called.
        """

        logger.debug('Handling submission response: is correct? %s. Challenge complete? %s' % ( is_correct, challenge_complete))

        self._callback.args = [is_correct, challenge_complete]

#         if is_correct.lower() == "true":
#             self._callback.State = State.PASSED
#         elif not challenge_complete.lower() == "true":
#             self._callback.State = State.FAILED
#         else:
#             pass # TODO
#             #TODO self._callback.State = neither State.PASSED nor State.FAILED
        self._callback.State = State.PASSED if is_correct.lower() == "true" else State.FAILED

    # --------------------------------------------------------------------------
    def shutdown(self,
              pin):
        """Prepares the station to power off.

        Sends the shutdown command to the station so it can clean up in
        preparation for power to be removed if the correct PIN is provided;
        otherwise, the reset request is ignored.

        Args:
            pin (int): This must be 31415 in order to reset the station.
        Returns:
            Empty JSON response with OK status code on success.
        Raises:
            N/A.

        """

        logger.debug('Received shutdown message from MS with json %s' % (json.dumps(request.json)))
        resp = jsonify()

        if pin == self._shutdownPin:
            logger.debug('Master server successfully requesting station shutdown with pin "%s"' % (pin))
            # TODO move elsewhere - maybe hw.py?
            sys_bus = dbus.SystemBus()
            ck_srv = sys_bus.get_object('org.freedesktop.ConsoleKit',
                                        '/org/freedesktop/ConsoleKit/Manager')
            ck_iface = dbus.Interface(ck_srv,
                                      'org.freedesktop.ConsoleKit.Manager')
            stop_method = ck_iface.get_dbus_method("Stop")

            if self._reallyShutdown:
                logger.info('Shutting down based on MS request')
                stop_method()
            else:
                logger.info('Shutdown successfully requested by MS but station not configured to really shutdown')

            resp.status_code = httplib.OK
        else:
            logger.warning('Master server requesting station shutdown with invalid pin "%s"' % (pin))
            resp.status_code = httplib.BAD_REQUEST

        return resp

# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO Delete
#TODO logger.setLevel(logging.INFO)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)
