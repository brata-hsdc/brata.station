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
Provides the definitions needed for the SECURE station type.
"""

from multiprocessing import Process
import logging
import logging.handlers
import sys
import time

#import random
import numpy
import pibrella

#import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import Image
import ImageDraw
import ImageFont

sys.path.append('/user/lib/python2.7/dist-packages')
import pygame

from station.interfaces import IStation
from station.state import State  # TODO: get rid of this dependency!!

# ------------------------------------------------------------------------------
class Station(IStation):
    """
    Provides the implementation for a SECURE station type. Supports tone
    generation, 128x32C I2C OLED display for messages, and reading the
    code via light pulses. The OLED display gives an Error message on the top
    line and a message on the bottom line. During tone generation, the current
    tone number is displayed. The pushbutton is used to advance to the next
    tone. Once the user generates a code, the photo detector circuit reads the
    pulse code. The circuit contains a red, green, and red LED. Green signifies
    ready to read, yellow signifies light detected, and red is set by the pi to
    acknoledge "Detected" pulse. The pibrella LEDs signify the SECURE station
    state, where RED=OFF, YELLOW=TONES, GREEN=PHOTODECTOR. 
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 config,
                 hwModule):
        """SECURE station constructor.

        Loads tone generation, display, and pulse read classes and configurations.

        Args:
            config:    a Config object containing properties to configure station characteristics
            hwModule:  python module object that defines hardware interfaces
        """
        logger.debug('Constructing SECURE')


        ledClassName = config.LedClassName
#        vibrationMotorClassName = config.VibrationMotorClassName
#        urgencyLedClassName = config.UrgencyLedClassName

        ledClass = getattr(hwModule, ledClassName)
        self._leds = {}

        for i in config.Leds:
            self._leds[i.Name] = ledClass(i.Name, i)
            # TODO: SS - Should I be placing the color from the config file here?

#        vibrationMotorClass = getattr(hwModule, vibrationMotorClassName)
#        urgencyLedClass = getattr(hwModule, urgencyLedClassName)

        self.ConnectionManager = None
        self.tonegen = None
 
    # --------------------------------------------------------------------------
    @property
    def stationTypeId(self):
        """Identifies this station's type as SECURE.

        Args:
            N/A.
        Returns:
            Station name as a string.
        Raises:
            N/A.

        """
        return "SECURE"

    # --------------------------------------------------------------------------
    def start(self):
        """ Station startup 

        Args:
            N/A
        Returns:
            N/A
        Raises:
            N/A

        """
        logger.info('Starting SECURE.')
        self._leds['red'].turnOn()
        self._leds['green'].turnOff()
        self._leds['yellow'].turnOff()
        # Turn on the display and blank the display
        self._display = LCDdisplay()

        logger.info('SECURE LCD Display Configured.')
        

    # --------------------------------------------------------------------------
    def stop(self, signal):
        """Station stop. Cleanup

        Args:
            signal - integer for system signal
        Returns:
            N/A
        Raises:
            N/A

        """
        self._leds['red'].turnOff()
        self._leds['green'].turnOff()
        self._leds['yellow'].turnOff()
        pibrella.output.h.off()
        self._display.display_message("      ", "     ")        

        logger.info('Received signal "%s". Stopping SECURE.', signal)

    # TODO. Turn off LEDs, pulse monitor, blank display

    # --------------------------------------------------------------------------
    def onReady(self):
        """Transition station to the Ready state

        Args:
            N/A.
        Returns:
            Station name as a string.
        Raises:
            N/A.

        """
        logger.info('SECURE transitioned to Ready state.')
        self._leds['red'].turnOn()
        self._leds['green'].turnOff()
        self._leds['yellow'].turnOff()
        # Blank the display
        self._display.display_message("      ", "READY")        


    # --------------------------------------------------------------------------
    def onProcessing(self,
                     args):
        """Transition station to the Processing state

        Args:
            args
        Returns:
            Station name as a string.
        Raises:
            N/A.

        """
        logger.info('SECURE transitioned to Processing state with args [%s].' % (args))

        self._leds['red'].turnOff()
        self._leds['yellow'].turnOn()
        self._leds['green'].turnOff()

        self._secure_tone_pattern = args
        if self.tonegen is None:
           self.tonegen = ToneGenerator(self._secure_tone_pattern, self._display)
           pibrella.button.pressed(self.tonegen.button_pressed)
        else:
            self.tonegen.stop()
            self.tonegen.reinit(self._secure_tone_pattern)
        logger.info('SECURE tonegen initialized')

    def onProcessing2(self, args):
        """Transition station to the Processing2 state

        Args:
            args
        Returns:
            Station name as a string.
        Raises:
            N/A.

        """
        logger.info('SECURE transitioned to Processing2 state.' )
        self.tonegen.stop()
        #pibrella.button.clear_events()
        self._leds['red'].turnOff()
        self._leds['yellow'].turnOff()
        self._leds['green'].turnOn()

        self._secure_code = args[0]
        rc = ReadCode(self._secure_code, self._display, self.ConnectionManager._callback)

        # wait for a code to be read
        self._display.display_message("      ", "TRANSMIT")
        t = Process(target = rc.run)
        t.start()
               

    # --------------------------------------------------------------------------
    def onProcessingCompleted(self, args):
        """Transition station to the ProcessingCompleted state

        This state will be entered when the graphics thread sets the state
        to ProcessingCompleted.

        Args:
            isCorrect
            Code
            errorMsg
        """
        
        logger.info('SECURE transitioned to ProcessingCompleted state.' )
        logger.info('TODO implement method body.' )
        isCorrect,code,error_msg = args
        self._error_msg = error_msg

        logger.debug('Submitted')
        logger.info('Submitting code: {} , match = {}, {}'.format(repr(code), isCorrect, error_msg))
        self.ConnectionManager.submit(candidateAnswer=code,
                                      isCorrect=isCorrect,
                                      failMessage=error_msg)

     

    # --------------------------------------------------------------------------
    def onFailed(self,
                 args):
        """Transition station to Failed state

        Args:
            args
        Returns:
            N/A.
        Raises:
            N/A.

        """
        logger.info('SECURE transitioned to Failed state with args [%s].' % (args))

        is_correct, challenge_complete = args
        # time.sleep(theatric_delay/1000.0)

        if challenge_complete.lower() == "true":
            logger.debug('Challenge complete.')
            self._display.display_message(self._error_msg, "FAILED")
            self._leds['red'].turnOn()
            self._leds['yellow'].turnOff()
            self._leds['green'].turnOff()
            pibrella.output.h.off()
        else:
            logger.debug('Challenge not complete. Turning on red LED')
            self._display.display_message(self._error_msg,"ERROR")
            self._leds['red'].turnOn()
            self._leds['yellow'].turnOff()
            self._leds['green'].turnOff()
            pibrella.output.h.off()


    # --------------------------------------------------------------------------
    def onPassed(self,
                 args):
        """Transition station to the Passed state

        Args:
            args
        Returns:
            N/A.
        Raises:
            N/A.


        """
        logger.info('SECURE transitioned to Passed state with args [%s].' % (args))
        self._display.display_message("     ", "PASSED")
        
        self._leds['red'].turnOff()
        self._leds['yellow'].turnOff()
        self._leds['green'].turnOn()
        pibrella.output.h.off()        

    # --------------------------------------------------------------------------
    def onUnexpectedState(self, value):
        """Attempted to transition to unexpected state

        Args:
            value
        Returns:
            N/A.
        Raises:
            N/A.

        """
        logger.critical('SECURE transitioned to Unexpected state %s', value)

 # ------------------------------------------------------------------------------
   
def parse_secure_error(argument):
    switcher = {
        0: "      ",
        1: "Timeout",
        2: "Short pulse width",
        4: "Long pulse width",
        8: ">Bits or <stop gap",
        16: "Long stop gap",
        32: "Failed"
        
    }
    return switcher.get(argument, "nothing")        

# ------------------------------------------------------------------------------
class LCDdisplay:
    """
    Generates the tones.
    """

    # --------------------------------------------------------------------------
    def __init__(self):
        """INIT
        """
    
        # Raspberry Pi pin configuration:
        self._RST = 22
        self._address = 0x3C

        # driver for 128x32 OLED display via I2C interface
        # self._disp = Adafruit_SSD1306.SSD1306_128_32(rst=self._RST)
        self._disp = Adafruit_SSD1306.SSD1306_128_64(rst=self._RST, i2c_address=self._address)
        # Initialize the didplay library.
        self._disp.begin()
        # Non-Invert display
        self._disp.command(0xA6)
        # Invert display
        #self._disp.command(0xA7)

        # Clear display.
        self._disp.clear()
        self._disp.display()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self._width = self._disp.width
        self._height = self._disp.height
        self._image = Image.new('1', (self._width, self._height))
        self._padding = 2
        self._top = self._padding
        self._bottom = self._height-self._padding
        # Get drawing object to draw on image.
        self._draw = ImageDraw.Draw(self._image)
        self._font_name = '/usr/share/fonts/truetype/freefont/FreeMono.ttf'
        self._font_top = ImageFont.truetype(self._font_name, 12)
        self._font_bot = ImageFont.truetype(self._font_name, 20)
        self.display_message('     ', 'READY')
        logger.debug('Constructing LCDdisplay')
    # --------------------------------------------------------------------------
    def __enter__(self):
        """ Enter """
        
        logger.debug('Entering LCDdisplay')
        return self

    # --------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        """ Exit """
        logger.debug('Exiting LCDdisplay')

    def display_message(self, Line1, Line2):
        # First define some constants to allow easy resizing of shapes.
        # Write two lines of text.
        self._draw.rectangle((0,0,self._width,self._height), outline=0, fill=0)
        x = self._padding
        self._draw.text((x, self._top+7),    Line1,  font=self._font_top, fill=255)
        self._draw.text((x, self._top+40), Line2,  font=self._font_bot, fill=255)

        # Display image.
        self._disp.clear()
        self._disp.display()
        self._disp.image(self._image.rotate(180))
        self._disp.display()


# ------------------------------------------------------------------------------
class ToneGenerator:
    """
    Generates the tones.
    """
    # --------------------------------------------------------------------------
    def __init__(self, tone_IDs, lcdDisplay):
        """INIT
        """
        # display messages for tones
        self._disp_msg = ["Tone #0",
                         "Tone #1",
                         "Tone #2",
                         "Tone #3",
                         "Tone #4",
                         "Tone #5",
                         "Tone #6",
                         "Tone #7",
                         "Tone #8",
                         "Tone #9"]

        self._bits        = 16       # audio resolution
        self._duration    = 10       # Length of audio playback
        self._sample_rate = 44100    # sample rate
        self._tone        = 0        # start out in tone 0 (off)

        # frequencies of tones
        #self._f = [44100, 276, 308, 340, 372, 404, 436, 468, 500]
        self._f = [44100, 300, 400, 500, 600, 700, 800, 900, 1000]

        # challenge tone IDs from MS
        tmp = tone_IDs[0]
        self._tone_ID = tmp[0:9]
        logger.debug('Challenge tone IDs = %s', self._tone_ID)
        self._tone_order = self._tone_ID
        # add the zero frequency (off) to the order list
        self._tone_order.insert(0, -1)
        logger.debug('Challenge tone IDs for list = %s', self._tone_order)
        # number of samples
        self._n_samples = int(round(self._duration*self._sample_rate))
        # init the mixer
        pygame.mixer.pre_init(44100, -self._bits, 2, 1024)
        pygame.init()

        #initialize the tones
        self._slist = [self.generate_sound(self._f[count]) for count in range(len(self._f))]
        #self._slist[self._tone].play(loops = -1)
        
        self._display = lcdDisplay
        self._display.display_message("      ", self._disp_msg[self._tone])
        logger.debug('Constructing Tone Generator')

    # --------------------------------------------------------------------------
    def __enter__(self):
        """ Enter """
        
        logger.debug('Entering Tone Generator')
        return self

    # --------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        """ Exit """
        logger.debug('Exiting Tone Generator')

#    def run(self)
#        _running = True
#        while _running:
#            pibrella.button.pressed.(self.button_pressed)
#            # TODO set _running to false if station state changes

    # --------------------------------------------------------------------------
    def reinit(self, tone_IDs):
        # challenge tone IDs from MS
        tmp = tone_IDs[0]
        self._tone_ID = tmp[0:9]
        logger.debug('Challenge tone IDs = %s', self._tone_ID)
        self._tone_order = self._tone_ID
        # add the zero frequency (off) to the order list
        self._tone_order.insert(0, -1)
        logger.debug('Challenge tone IDs for list = %s', self._tone_order)
        self._display.display_message("      ", self._disp_msg[self._tone])
        logger.debug('Constructing Tone Generator')


    def generate_sound(self, freq):

        #setup our numpy array to handle 16 bit ints, which is what we set our
        #mixer to expect
        buf = numpy.zeros((self._n_samples, 2), dtype = numpy.int16)
        max_sample = 2**(self._bits - 1) - 1

        t = numpy.arange(self._n_samples)/float(self._sample_rate )
        buf[:,0] = max_sample*numpy.sin(2*numpy.pi*freq*t)
        buf[:,1] = buf[:,0]
        return pygame.sndarray.make_sound(buf)

    def button_pressed(self, pin):
        self.change_tones()
        logger.debug('ToneGenerator Button Pressed')

    def change_tones(self):
        self._slist[(self._tone_order[self._tone]+1)].stop() # stop the current tone
        self._tone = self._tone + 1
        if self._tone == (len(self._tone_order)): # go back to the beginning
            self._tone = 0
        self._slist[(self._tone_order[self._tone]+1)].play(loops = -1)
        logger.debug('Tone ID = %d', (self._tone_order[self._tone]))
        logger.debug('Tone = %d', self._tone)
        logger.debug('length = %d', len(self._tone_order))
        self._display.display_message("      ", self._disp_msg[self._tone])

    def stop(self):
        self._slist[(self._tone_order[self._tone]+1)].stop() # stop the current tone
        self._tone = 0
        self._display.display_message("      ", "      ")


    # --------------------------------------------------------------------------

# ------------------------------------------------------------------------------
class ReadCode:
    """
    Read the pulse code.
    """


    # --------------------------------------------------------------------------
    def __init__(self, tone_IDs, display, CM):
        """INIT
        """
        self._display = display
        #turn on the light sensor
        pibrella.output.h.on()

        # These could be put in the config file
        self._stoprange = [2, 5]    # minimum and maximum number of stop gaps between symbols
        self._nsymbols = 4          # number of symbols in the code
        self._pulserange = [0.200*0.8, 0.250*1.2] # acceptable pulsewidth range
        self._secure_timeout = 30.0 # timeout in seconds
        self._secure_code = []      # expected secure code
        self._maxcount = 7          # maximum symbol value

        # other variables
        self._light_on = 0          # Has the light (pulse) already been on
        self._count = 0             # count of the current symbol

        self._scount = 0            # count of the number of symbols
        self._pulse_start = 0       # Pulse leading edge counter.
        self._t1 = 0                # Time of pulse 1 leading edge
        self._t2 = 0                # Time of pulse 2 leading edge
        self._pulse_period = 0      # pulse period
        self._pulse_width = 0       # pulse width
        self._ctime = 0             # current time
        self._ttime = 0             # trailing time
        self._code = []             # the transmitted code
        self._ERROR = 0             # error flag
        self._tone_ID = tone_IDs    # expected code

        self._ConnectionManager = CM # Connection Manager

        logger.debug('Constructing Code Reader with tone_IDs %s' % tone_IDs)

    # --------------------------------------------------------------------------
    def __enter__(self):
        """ Enter """
        
        logger.debug('Entering Code Reader')
        return self

    # --------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        """ Exit """
        logger.debug('Exiting Code Reader')

    def parse_secure_error(self, argument):
        switcher = {
            0: "Passed",
            1: "Timeout",
            2: "Pulse width too small",
            4: "Pulse width too large",
            8: "Symbol too long or stop gap too small",
            16: "Stop gap too large",
            32: "Failed"
            
        }
        return switcher.get(argument, "nothing")

    def check_code(self):
        # the tone IDs of 0, 1, 3, and 4 correspond to the desired code
        # desiredcode = [ self._tone_ID[i] for i in [0, 1, 3, 4]]

        desiredcode = self._tone_ID
        return cmp(desiredcode, self._code)
        
    def run(self):
        self._stime = time.time()   # start time
        logger.debug('Read in a code transmitted via light in a pulse train')
#        self._display.display_message("      ", "RUN")
        
        #loop until the number of symbols in a word are received
        #TODO: replace the button read with the submit code QR
        while (pibrella.button.read() != 1 and self._scount<self._nsymbols):
            # check if an error has occured
            if (self._ERROR):
                break
            # check if we need to timeout because of inactivity
            if ((time.time() - self._stime) > self._secure_timeout):
                self._ERROR = self._ERROR + 1
                break
            # Read pibrella inputs and do something for on or off
            if pibrella.input.d.read() == 1:
                # Trigger at the leading edge of the pulse
                if self._light_on == 0:
                    if self._pulse_start == 0:
                        t1 = time.time()
                    elif self._pulse_start == 1:
                        t2 = time.time()
                        self._pulse_period = t2 - t1 # time between first two pulses
                        self._pulse_width = self._pulse_period/2.0
                        # check pulse width size
                        if (self._pulse_width < self._pulserange[0]):
                            logger.debug("Pulse width %f ms" % (self._pulse_width*1000))
                            self._ERROR = self._ERROR + 2
                        elif (self._pulse_width > self._pulserange[1]):
                            self._ERROR = self._ERROR + 4
                            logger.debug("Pulse width %f ms" % (self._pulse_width*1000))
                    else:
                        self._count = self._count + 1
                    self._light_on = 1
                    self._pulse_start = self._pulse_start + 1
                    logger.debug("pulse start %d" % self._pulse_start)

            else:
                # get the current time
                self._ctime = time.time()
                # trailing edge of pulse
                if self._light_on == 1:
                    self._light_on = 0
                    self._ttime = self._ctime # time of trailing edge

                else:
                    # check to make sure we read the first two pulses
                    if (self._pulse_start >= 2):                              
                        # if off time is greater than the number of stop bits
                        if ((self._ctime-self._ttime) > (self._pulse_width*self._stoprange[0]+self._pulse_width)):
                            logger.debug("stop gap = %f ms" % ((self._ctime-self._ttime)*1000))
                            logger.debug("stoprange = %f ms" % (self._pulse_width*self._stoprange[0]*1000))
                            logger.debug("The Pulse count is %d" % self._count)
                            # error if the symbol is out of range
                            if self._count > self._maxcount:
                                    self._ERROR = self._ERROR + 8
                            self._code.append(self._count) # convert to char
                            self._count = 0
                            self._pulse_start = 0
                            self._scount = self._scount + 1
                    else:
                        # check if stop gap is too large
                        if (self._scount > 0):
                            if (self._ctime-self._ttime) > (self._pulse_width*self._stoprange[1]+self._pulse_width):
                                self._ERROR = self._ERROR + 16


        if self._ERROR:
            logger.debug('Error: ' + self.parse_secure_error(self._ERROR))
        else:
            logger.debug('The code is ' + ''.join(chr(i+48) for i in self._code).strip('[]'))
            logger.debug('The period is %f ms' % (self._pulse_period*1000.0))
            logger.debug('The pulse width is %f ms' % (self._pulse_period/2*1000.0))
            # TODO check code received against transmitted code
            if (abs(self.check_code()) > 0):
                self._ERROR = self._ERROR + 32
                logger.debug('Error: ' + self.parse_secure_error(self._ERROR))

        if (self._ERROR>0):
            isCorrect = "False"
        else:
            isCorrect = "True"

        logger.debug('Pre Connection Manager')
 
        self._ConnectionManager.args = (isCorrect, self._code, self.parse_secure_error(self._ERROR))
        logger.debug('Post Connection Manager {}'.format(self._ConnectionManager.State))

        self._ConnectionManager.State = State.PROCESSING_COMPLETED
        logger.debug('State Change Connection Manager {}'.format(self._ConnectionManager.State))

        return self._code, self._ERROR, self.parse_secure_error(self._ERROR)
            

# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

