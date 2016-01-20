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
Extract the Raspberry Pi serial number, which should uniquely identify a station
"""
from __future__ import print_function

#----------------------------------------------------------------------------
class PiSerial(object):
    """ This class parses the /proc/cpuinfo contents to extract the
        serial number of the host.
    """
    cachedSerialNumber = None
    
    @staticmethod
    def serialNumber():
        """ Read /proc/cpuinfo.  Find and return the serial number.
        
            Returns:  the serial number, as a string; or "0" if no
                      serial number is found
        """
        if PiSerial.cachedSerialNumber is None:
            PiSerial.cachedSerialNumber = "0"
            with open("/proc/cpuinfo", "r") as cpuInfo:
                for line in cpuInfo:
                    line = line.strip().split()
                    if len(line) > 2 and line[0] == "Serial" and line[1] == ":":
                        PiSerial.cachedSerialNumber = line[2]
        return PiSerial.cachedSerialNumber

#----------------------------------------------------------------------------
if __name__ == "__main__":
    serial = PiSerial.serialNumber()
    print("Serial number: {}".format(serial))
    