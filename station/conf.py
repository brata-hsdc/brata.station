import logging
import logging.handlers


# ------------------------------------------------------------------------------
class StationConfig:

   # ---------------------------------------------------------------------------
   def __init__(self):
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


      self.StationTypeConfig = StationTypeConfig()


# ------------------------------------------------------------------------------
class StationTypeConfig:

   # ---------------------------------------------------------------------------
   def __init__(self):
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

   # ---------------------------------------------------------------------------
   def __init__(self,
                name):
      self.Name = name
      logger.debug('Constructing LED %s config', self.Name)


# ------------------------------------------------------------------------------
class VibrationMotorConfig:

   # ---------------------------------------------------------------------------
   def __init__(self,
                name,
                onDuration_s,
                offDuration_s):
      self.Name = name
      logger.debug('Constructing vibration motor %s config', self.Name)
      self.OnDuration_s = onDuration_s
      self.OffDuration_s = offDuration_s

# ------------------------------------------------------------------------------
class ConnectionManagerConfig:

   # ---------------------------------------------------------------------------
   def __init__(self):
      logger.debug('Constructing Connection Manager config')
      self.StationInstanceId = '01'
      self.StationType = 'HMB'

      self.MasterServerProtocol = 'http'
      self.MasterServerHost = 'localhost'
      self.MasterServerPort = '8080'
      self.MasterServerBasePath = '/ms/1.0.0'

      self.Connect = 'connect'
      self.Disconnect = 'disconnect'
      self.TimeExpired = 'time_expired'

   # ---------------------------------------------------------------------------
   @property
   def BaseUrl(self):
      result = "%s://%s:%s%s" % (self.MasterServerProtocol,
                                 self.MasterServerHost,
                                 self.MasterServerPort,
                                 self.MasterServerBasePath)
      return result

   # ---------------------------------------------------------------------------
   @property
   def ConnectUrl(self):
      result = "%s/%s" % (self.BaseUrl, self.Connect)
      return result

   # ---------------------------------------------------------------------------
   @property
   def DisconnectUrl(self):
      result = "%s/%s" % (self.BaseUrl, self.Disconnect)
      return result

   # ---------------------------------------------------------------------------
   @property
   def TimeExpiredUrl(self):
      result = "%s/%s" % (self.BaseUrl, self.TimeExpired)
      return result


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

