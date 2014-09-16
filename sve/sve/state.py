import logging
import logging.handlers


# ------------------------------------------------------------------------------
class State:

   READY, PROCESSING, FAILED, PASSED = range(4)


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)


