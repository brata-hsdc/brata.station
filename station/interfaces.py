from abc import ABCMeta, abstractmethod
import logging
import logging.handlers


# ------------------------------------------------------------------------------
class IConnectionManager:
    __metaclass__ = ABCMeta

    # --------------------------------------------------------------------------
    @abstractmethod
    def run(self):
        pass

    # --------------------------------------------------------------------------
    @abstractmethod
    def startListening(self):
        pass

    # --------------------------------------------------------------------------
    @abstractmethod
    def stopListening(self):
        pass


# ------------------------------------------------------------------------------
class ILed:
    __metaclass__ = ABCMeta

    # --------------------------------------------------------------------------
    @abstractmethod
    def turnOff(self):
        pass

    # --------------------------------------------------------------------------
    @abstractmethod
    def turnOn(self):
        pass

    # --------------------------------------------------------------------------
    @abstractmethod
    def setFlashing(self):
        pass


# ------------------------------------------------------------------------------
class IStation:
    __metaclass__ = ABCMeta

    # --------------------------------------------------------------------------
    @abstractmethod
    def start(self):
        pass

    # --------------------------------------------------------------------------
    @abstractmethod
    def stop(self, signal):
        pass

    # --------------------------------------------------------------------------
    @abstractmethod
    def onReady(self):
        pass

    # --------------------------------------------------------------------------
    @abstractmethod
    def onProcessing(self):
        pass

    # --------------------------------------------------------------------------
    @abstractmethod
    def onFailed(self):
        pass

    # --------------------------------------------------------------------------
    @abstractmethod
    def onPassed(self):
        pass

    # --------------------------------------------------------------------------
    @abstractmethod
    def onUnexpectedState(self, value):
        pass


# ------------------------------------------------------------------------------
class IVibrationMotor:
    __metaclass__ = ABCMeta

    # --------------------------------------------------------------------------
    @abstractmethod
    def start(self):
        pass

    # --------------------------------------------------------------------------
    @abstractmethod
    def stop(self):
        pass


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

