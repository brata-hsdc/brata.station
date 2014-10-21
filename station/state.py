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
Provides enumerated types to represent state values.
"""

import logging
import logging.handlers


# ------------------------------------------------------------------------------
class State:
    """
    The states of the station representing whether the station is ready to
    accept a challenge, processing a challenge, or has completed a challenge
    with a failed or passed indicator.
    """

    READY, PROCESSING, FAILED, PASSED = range(4)


# ------------------------------------------------------------------------------
class HttpMethod:
    """
    HTTP verbs used for REST calls.
    """

    GET, PUT, POST, DELETE = range(4)


# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)


