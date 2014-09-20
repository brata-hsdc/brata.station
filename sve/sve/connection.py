from sve.interfaces import IConnectionManager
from sve.state import HttpMethod
import json
import logging
import logging.handlers
import requests
import sys
from threading import Thread
from time import sleep
import traceback
## TODO Delete
#import pprint


# ------------------------------------------------------------------------------
class ConnectionManager(IConnectionManager):

   # ---------------------------------------------------------------------------
   def __init__(self,
                config):

      # TODO?
      """
   def __init__(self,
                todoHandler,
                config):
      """

      logger.debug('Constructing connection manager')
      self._connectUrl = config.ConnectUrl
      self._connected = False
      self._listening = False
      self._timeToExit = False
      #TODO? self._handler = todoHandler
      self._thread = Thread(target = self.run)
      self._thread.daemon = True
      self._thread.start()

   # ---------------------------------------------------------------------------
   @property
   def _connected(self):
      return self._connectedValue

   @_connected.setter
   def _connected(self,
                  value):
      self._connectedValue = value
      logger.info('Is connection manager connected? %s' % (value))

   # ---------------------------------------------------------------------------
   def __enter__(self):
      logger.debug('Entering connection manager')
      return self

   # ---------------------------------------------------------------------------
   def __exit__(self, type, value, traceback):
      logger.debug('Exiting connection manager')
      stopListening(self)
      self._timeToExit = True
      self._thread.join()

   # ---------------------------------------------------------------------------
   def run(self):
      logger.debug('Starting TODO thread for connection manager')

      while not self._timeToExit:
         try:
            if self._listening:

               if (not self._connected):
                  self.connect()
                  self._connected = True

               # TODO
               #pass

            sleep(1)
         except Exception, e:
            exType, ex, tb = sys.exc_info()
            logging.critical("Exception occurred of type " + exType.__name__)
            logging.critical(str(e))
            traceback.print_tb(tb)

   # ---------------------------------------------------------------------------
   def startListening(self):
      logger.debug('Starting listening for connection manager')
      # TODO
      self._listening = True

   # ---------------------------------------------------------------------------
   def stopListening(self):
      logger.debug('Stopping listening for connection manager')
      self._listening = False
      self._connected = False

   # ---------------------------------------------------------------------------
   def callService(self,
                   httpMethod,
                   endpointUrl,
                   args):
      logger.debug('Calling service with HTTP method %s, endpoint URL %s, and args %s' % (httpMethod, endpointUrl, args))
      data = json.dumps(args)
      response = requests.post(endpointUrl, data)
      # TODO[WE ARE HERE]
      ##response = requests.post(endpointUrl, data, auth=('user', '*****'))

      #logger.debug('Service response: %s' % (response))
      #logger.debug('Service response: %s' % (vars(response)))
      #pprint.pprint(vars(response))
      #logger.debug('Service response.text: %s' % (response.text))
      logger.debug('Service response status_code: %s' % (response.status_code))
      logger.debug('Service response.name1: %s' % (response.json['name1']))
      logger.debug('Service response.name2: %s' % (response.json['name2']))


   # ---------------------------------------------------------------------------
   def connect(self):
      logger.debug('Connection manager connecting')
      self.callService(HttpMethod.POST, self._connectUrl, {'name': 'test',
                                                           'desc': 'foobar'})


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)
