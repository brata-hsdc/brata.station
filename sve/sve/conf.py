import logging
import logging.handlers


# ------------------------------------------------------------------------------
class SveConfig:

   # ---------------------------------------------------------------------------
   def __init__(self):
      logger.debug('Constructing SVE config')

      #---
      # Enable one of the following for the hardware. The console module
      # simulates the hardware using console functions. This means the push
      # button will be simulated by the space bar, and LEDs and vibration motor
      # status will be printed to the logs.
      #---
      self.HardwareModuleName = 'sve.console'
      #self.HardwareModuleName = 'sve.hw'

      # JIA TODO BEGIN addition
      #---
      # Enable one of the following for the connection. TODO Blah blah blah.
      #---
      #self.ConnectionModuleName = 'sve.console'
      self.ConnectionModuleName = 'sve.connection'
      # JIA TODO END addition

#TODO Delete      self.PushButtonClassName = 'PushButton'
      self.LedClassName = 'Led'
      self.VibrationMotorClassName = 'VibrationMotor'

      # JIA TODO BEGIN addition
      self.ConnectionManagerClassName = 'ConnectionManager'
      # JIA TODO END addition

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

#TODO Delete      self.PushButton = PushButtonConfig()

      # JIA TODO BEGIN addition
      self.ConnectionManager = ConnectionManagerConfig()
      # JIA TODO END addition


# ------------------------------------------------------------------------------
class LedConfig:

   # ---------------------------------------------------------------------------
   def __init__(self,
                name):
      self.Name = name
      logger.debug('Constructing LED %s config', self.Name)


#TODO Delete, clean up imports
## ------------------------------------------------------------------------------
#class PushButtonConfig:
#
#   # ---------------------------------------------------------------------------
#   def __init__(self):
#      logger.debug('Constructing push button config')


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

# JIA TODO BEGIN addition
# ------------------------------------------------------------------------------
class ConnectionManagerConfig:

   # ---------------------------------------------------------------------------
   def __init__(self):
      logger.debug('Constructing Connection Manager config')
      self.MasterServerProtocol = 'http'
      self.MasterServerHost = 'localhost'
      self.MasterServerPort = '9876'
      self.MasterServerBasePath = '/ms/1.0.0'

      self.Connect = 'connect'

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
# JIA TODO END addition


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

