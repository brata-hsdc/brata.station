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


# ------------------------------------------------------------------------------
class ConnectionManager(IConnectionManager):
    """
    TODO class comment
    """

    _app = Flask(__name__)
    _callback = None


    # --------------------------------------------------------------------------
    def __init__(self,
                 station,
                 stationTypeId,
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
        self._joinUrl = config.JoinUrl
        self._disconnectUrl = config.DisconnectUrl
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

        self._callback = station
        #TODO? self._handler = todoHandler

        self._app.add_url_rule(config.ResetUrlRule,
                               'reset',
                               self.reset,
                               methods=['POST'])

        self._app.add_url_rule(config.StartChallengeUrlRule,
                               'start_challenge',
                               self.startChallenge,
                               methods=['POST'])

        self._app.add_url_rule(config.HandleSubmissionUrlRule,
                               'handle_submission',
                               self.handleSubmission,
                               methods=['POST'])

        self._app.add_url_rule(config.ShutdownUrlRule,
                             'shutdown',
                             self.shutdown,
                             methods=['POST'])

        self._thread = Thread(target = self.run)
        self._thread.daemon = True
        self._thread.start()

    # --------------------------------------------------------------------------
    @property
    def _connected(self):
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
        return self._connectedValue

    @_connected.setter
    def _connected(self,
                  value):
        self._connectedValue = value
        logger.info('Is connection manager connected? %s' % (value))

    # --------------------------------------------------------------------------
    def __enter__(self):
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
        logger.debug('Entering connection manager')
        return self

    # --------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
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
        logger.debug('Exiting connection manager')
        stopListening(self)
        self._timeToExit = True
        self._thread.join()

    # --------------------------------------------------------------------------
    def run(self):
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
        logger.info('Starting TODO thread for connection manager')

        while not self._timeToExit:
            try:
                logger.debug('Loop begin for connection manager')
                if self._listening:

                    if (not self._connected):
                        self.join()
                        self._connected = True

                        # TODO named constant
                        port = 5000
                        server = HTTPServer(WSGIContainer(self._app))
                        server.listen(port)
                        IOLoop.instance().start()
                    # TODO
                    #pass

                sleep(1)
            except requests.ConnectionError, e:
                logger.critical(str(e))
                # TODO nothing to do - cannot connect because remote end is not up;
                # just wait and try again later
                # TODO configurable sleep time...
                sleep(3)
            except Exception, e:
                exType, ex, tb = sys.exc_info()
                logger.critical("Exception occurred of type %s: %s" % (exType.__name__, str(e)))
                traceback.print_tb(tb)

        self.disconnect()
        logger.info('Stopping TODO thread for connection manager')

    # --------------------------------------------------------------------------
    def startListening(self):
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
        logger.debug('Starting listening for connection manager')
        # TODO
        self._listening = True

    # --------------------------------------------------------------------------
    def stopListening(self):
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
        logger.debug('Stopping listening for connection manager')
        self._listening = False
        self._connected = False


    # --------------------------------------------------------------------------
    def timestamp(self):
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
        ts = time()
        st = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        return st


    # --------------------------------------------------------------------------
    def callService(self,
                    httpMethod,
                    endpointUrl,
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
        # TODO check if args present - might be null/empty
        args['message_timestamp'] = self.timestamp()
        logger.debug('Calling service with HTTP method %s, endpoint URL %s, and args %s' % (httpMethod, endpointUrl, args))
        data = json.dumps(args)
        response = requests.post(endpointUrl, data)

        # TODO Delete
        ##response = requests.post(endpointUrl, data, auth=('user', '*****'))

        logger.debug('Service returned %s for HTTP method %s, endpoint URL %s, and args %s' % (response.status_code, httpMethod, endpointUrl, args))
        return (response.status_code, response.json)


    # ===
    # Messages from Station to MS
    # ===

    # --------------------------------------------------------------------------
    def join(self):
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
        logger.debug('Station requesting join with master server')
        url = self._joinUrl
        (status, response) = self.callService(
            HttpMethod.POST, url,
            {
                'message_version'  : 0,
                'message_timestamp': self.timestamp(),
                'station_id'       : self._stationId,
                'station_type'     : self._stationType,
                'station_url'      : 'http://todo:5000/rpi/blah/blah/blah'
            })

        if status == httplib.OK:
            logger.debug('Service %s returned OK' % (url))
        elif status == httplib.NOT_FOUND:
            logger.critical('Service %s returned NOT_FOUND' % (url))
        else:
            logger.critical('Unexpected HTTP response %s received from service %s' % (status, url))


    # --------------------------------------------------------------------------
    def disconnect(self):
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
        logger.debug('Station requesting disconnect from master server')
        url = self._disconnectUrl
        (status, response) = self.callService(
            HttpMethod.POST,
            "{}/{}".format(url, self._stationId),
            {})

        if status == httplib.OK:
            logger.debug('Service %s returned OK' % (url))
        elif status == httplib.NOT_FOUND:
            logger.critical('Service %s returned NOT_FOUND' % (url))
        else:
            logger.critical('Unexpected HTTP response %s received from service %s' % (status, url))


    # --------------------------------------------------------------------------
    def timeExpired(self):
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
        logger.debug('Station informing master server that time for challenge has expired')

        theatric_delay_ms = 0
        candidate_answer = 0

        url = self._timeExpiredUrl
        (status, response) = self.callService(
            HttpMethod.POST,
            "{}/{}".format(url, self._stationId),
            {})

        if status == httplib.OK:
            logger.debug('Service %s returned OK' % (url))
        elif status == httplib.NOT_FOUND:
            logger.critical('Service %s returned NOT_FOUND' % (url))
        else:
            logger.critical('Unexpected HTTP response %s received from service %s' % (status, url))

        self._callback.args = [theatric_delay_ms, candidate_answer]
        self._callback.State = State.FAILED


    # --------------------------------------------------------------------------
    def submitCtsComboToMS(self):
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
        logger.debug('Station submitting answer to master server')
        url = self._submitUrl
        (status, response) = self.callService(
            HttpMethod.POST, url,
            {
                'message_version'            : 0,
                'message_timestamp'          : self.timestamp(),
                'station_id'                 : self._stationId,
                'candidate_answer'           : (31, 41, 59),
                'is_correct'                 : "True"
            }) # TODO

        if status == httplib.OK:
            logger.debug('Service %s returned OK' % (url))
        elif status == httplib.NOT_FOUND:
            logger.critical('Service %s returned NOT_FOUND' % (url))
        else:
            logger.critical('Unexpected HTTP response %s received from service %s' % (status, url))


    # --------------------------------------------------------------------------
    def submitCpaDetectionToMS(self,
                               hitDetected):
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
        logger.debug('Station submitting answer to master server')
        url = self._submitUrl
        (status, response) = self.callService(
            HttpMethod.POST, url,
            {
                'message_version'            : 0,
                'message_timestamp'          : self.timestamp(),
                'station_id'                 : self._stationId,
                'hit_detected_within_window' : hitDetected,
                'is_correct'                 : "True" # TODO
            })

        if status == httplib.OK:
            logger.debug('Service %s returned OK' % (url))
        elif status == httplib.NOT_FOUND:
            logger.critical('Service %s returned NOT_FOUND' % (url))
        else:
            logger.critical('Unexpected HTTP response %s received from service %s' % (status, url))


    # ===
    # Messages from MS to Station
    # ===

    # --------------------------------------------------------------------------
    def reset(self,
              pin):
        """Transitions the station to the Ready state.

        Transiitions the station to the Ready state if the correct PIN is
        provided; otherwise, the reset request is ignored.

        Args:
            pin (int): This must be 31415 in order to reset the station.
        Returns:
            Empty JSON response with 200 status code on success.
        Raises:
            N/A.

        """

        resp = jsonify()

        if pin == self._resetPin:
            logger.debug('Master server successfully requesting station reset with pin "%s"' % (pin))
            self._callback.State = State.READY
            resp.status_code = 200
        else:
            logger.debug('Master server requesting station reset with invalid pin "%s"' % (pin))
            resp.status_code = 400

        return resp


    # --------------------------------------------------------------------------
    def startChallenge(self,
                       teamId):
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

        # TODO...
        #if not request.json or not 'title' in request.json:
        if not request.json:
            #TODO abort(400)
            logger.debug('return 400?')

        message_version = request.json['message_version']
        message_timestamp = request.json['message_timestamp']
        theatric_delay_ms = request.json['theatric_delay_ms']

        if 'hmb_vibration_pattern_ms' in request.json:
            logger.debug('Received a start_challenge request for HMB station')
            hmb_vibration_pattern_ms = request.json['hmb_vibration_pattern_ms']
            self._callback.args = hmb_vibration_pattern_ms
            logger.debug('Master server requesting station start_challenge (ver %s) for team ID %s at %s with theatric delay of %s ms, HMB vibration pattern %s' % (message_version, teamId, message_timestamp, theatric_delay_ms, hmb_vibration_pattern_ms))
        elif 'cpa_velocity' in request.json:
            logger.debug('Received a start_challenge request for CPA station')
            cpa_velocity = request.json['cpa_velocity']
            cpa_velocity_tolerance_ms = request.json['cpa_velocity_tolerance_ms']
            cpa_window_time_ms = request.json['cpa_window_time_ms']
            cpa_window_time_tolerance_ms = request.json['cpa_window_time_tolerance_ms']
            cpa_pulse_width_ms = request.json['cpa_pulse_width_ms']
            cpa_pulse_width_tolerance_ms = request.json['cpa_pulse_width_tolerance_ms']
            self._callback.args = [cpa_velocity, cpa_velocity_tolerance_ms, cpa_window_time_ms, cpa_window_time_tolerance_ms, cpa_pulse_width_ms, cpa_pulse_width_tolerance_ms]
            logger.debug('Master server requesting station start_challenge (ver %s) for team ID %s at %s with theatric delay of %s ms, CPA velocity %s with tolerance %s, window time %s ms with tolerance %s ms, and pulse width %s ms with tolerance %s ms' % (message_version, teamId, message_timestamp, theatric_delay_ms, cpa_velocity, cpa_velocity_tolerance_ms, cpa_window_time_ms, cpa_window_time_tolerance_ms, cpa_pulse_width_ms, cpa_pulse_width_tolerance_ms))
        elif 'cts_combo' in request.json:
            logger.debug('Received a start_challenge request for CTS station')
            cts_combo = request.json['cts_combo']
            self._callback.args = cts_combo
            logger.debug('Master server requesting station start_challenge (ver %s) for team ID %s at %s with theatric delay of %s ms, CTS combo %s' % (message_version, teamId, message_timestamp, theatric_delay_ms, cts_combo))
        else:
            logger.critical('Received a start_challenge request for unrecognized station')

        # TODO...

        # TODO implement method body
        self._callback.State = State.PROCESSING

        # TODO can't pass-in self - how to get handle to self? is it needed?

        # TODO
        resp = jsonify({'foo': 'bar'})
        resp.status_code = 200
        return resp



    # --------------------------------------------------------------------------
    def handleSubmission(self,
                         stationId,
                         teamId):
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

        # TODO...
        #if not request.json or not 'title' in request.json:
        if not request.json:
            #TODO abort(400)
            logger.debug('return 400?')

        message_version = request.json['message_version']
        message_timestamp = request.json['message_timestamp']
        theatric_delay_ms = request.json['theatric_delay_ms']
        candidate_answer = request.json['candidate_answer']
        is_correct = request.json['is_correct']
        challenge_incomplete = request.json['challenge_incomplete']

        logger.debug('Master server relaying (ver %s) user answer to station ID %s for team ID %s at %s. Answer "%s" with theatric delay %s ms is correct? %s. Challenge incomplete? %s' % (message_version, stationId, teamId, message_timestamp, candidate_answer, theatric_delay_ms, is_correct, challenge_incomplete))

        self._callback.args = [theatric_delay_ms, candidate_answer]

        if is_correct:
            self._callback.State = State.PASSED
        elif challenge_incomplete:
            self._callback.State = State.FAILED
        else:
            pass # TODO
            #TODO self._callback.State = neither State.PASSED nor State.FAILED

        # TODO
        resp = jsonify({'foo': 'bar'})
        resp.status_code = 200
        return resp


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
            Empty JSON response with 200 status code on success.
        Raises:
            N/A.

        """
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

            resp.status_code = 200
        else:
            logger.debug('Master server requesting station shutdown with invalid pin "%s"' % (pin))
            resp.status_code = 400

        return resp


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)
