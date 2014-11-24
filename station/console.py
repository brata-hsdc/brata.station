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

from collections import namedtuple
import logging
import logging.handlers
import sys
from threading import Thread
from time import sleep
import traceback

from station.interfaces import IDisplay
from station.interfaces import ILed
from station.interfaces import IPushButtonMonitor
from station.interfaces import IVibrationMotor
from station.interfaces import IBuzzer
from station.interfaces import IInput
from station.util import NonBlockingConsole
import station.util
from mido import MidiFile
import os

# ------------------------------------------------------------------------------
class Display(IDisplay):
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self,
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
        logger.debug('Constructing display')

        self._line1Text = ''
        self._line2Text = ''

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
        logger.debug('Entering display')
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
        logger.debug('Exiting display')
        self.setText('')

    # --------------------------------------------------------------------------
    def setLine1Text(self,
                     text):
        """Sets the text for line 1 of the display.

        Sets the text for line 1 of the display. If the text is too long to fit
        on the display, then the text scrolls over time.

        Args:
            text (string): The text to display.
        Returns:
            N/A.
        Raises:
            N/A.

        """
        self._line1Text = text
        logger.debug('Setting Line 1 text. Display now reads "%s"[br]"%s"' %
                     (self._line1Text, self._line2Text))


    # --------------------------------------------------------------------------
    def setLine2Text(self,
                     text):
        """Sets the text for line 2 of the display.

        Sets the text for line 2 of the display. If the text is too long to fit
        on the display, then the text scrolls over time.

        Args:
            text (string): The text to display.
        Returns:
            N/A.
        Raises:
            N/A.

        """
        self._line2Text = text
        logger.debug('Setting Line 2 text. Display now reads "%s"[br]"%s"' %
                     (self._line1Text, self._line2Text))


    # --------------------------------------------------------------------------
    def setText(self,
                text):
        """Sets the text for the entire display.

        Directly sets the text for the display. Multiple lines can be provided
        at once by separating with a '\n' character.

        Args:
            text (string): The text to display.
        Returns:
            N/A.
        Raises:
            N/A.

        """
        idx = text.find('\n')

        if idx != -1:
            self._line1Text = text[:idx]
            self._line2Text = text[idx+1:]
        else:
            self._line1Text = text
            self._line2Text = ''

        logger.debug('Setting Line 2 text. Display now reads "%s"[br]"%s"' %
                     (self._line1Text, self._line2Text))


# ------------------------------------------------------------------------------
class Led(ILed):
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 name,
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
        self.Name = name + " (" + config.OutputPin +")"
        logger.debug('Constructing LED %s', self.Name)

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
        logger.debug('Entering LED %s', self.Name)
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
        logger.debug('Exiting LED %s', self.Name)
        self.turnOff()

    # --------------------------------------------------------------------------
    def turnOff(self):
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
        logger.debug('Turning off LED %s', self.Name)

    # --------------------------------------------------------------------------
    def turnOn(self):
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
        logger.debug('Turning on LED %s', self.Name)

    # --------------------------------------------------------------------------
    def setFlashing(self):
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
        logger.debug('Set LED %s flashing', self.Name)


# ------------------------------------------------------------------------------
PushButton = namedtuple('PushButton', 'Name Handler')


# ------------------------------------------------------------------------------
class PushButtonMonitor(IPushButtonMonitor):
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self):
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
        logger.debug('Constructing push button monitor')
        self._pushButtons = {}
        self._listening = False
        self._timeToExit = False
        self._thread = Thread(target = self.run)
        self._thread.daemon = True
        self._thread.start()

    # --------------------------------------------------------------------------
    def __enter__(self):
        logger.debug('Entering push button monitor')
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
        logger.debug('Exiting push button monitor')
        self.stopListening()
        self._timeToExit = True
        self._thread.join()

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
        logger.debug('Starting listening for push button monitor')
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
        logger.debug('Stopping listening for push button monitor')
        self._listening = False

    # --------------------------------------------------------------------------
    def registerPushButton(self,
                           name,
                           buttonPressHandler,
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
        keypress = config.ConsoleKeyPress

        if keypress in self._pushButtons:
            logger.warning('Console key [%s] already registered to push button %s; redefining to register to push button %s' %
                           (keypress, self._pushButtons[keypress].Name, name))

        self._pushButtons[keypress] = PushButton(name, buttonPressHandler)

        logger.debug('Registered push button %s for key press [%s]' %
                     (name, keypress))

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
        with NonBlockingConsole() as nbc:
            logger.debug('Starting key press thread for push button monitor')

            while not self._timeToExit:
                try:
                    if self._listening:
                        keypress = nbc.get_data()

                        if keypress in self._pushButtons:
                            pb = self._pushButtons[keypress]

                            logger.debug('Received key press event [%s] from push button monitor for push button %s' % (keypress, pb.Name))
                            pb.Handler(pb.Name)

                        elif keypress != False:
                            logger.warning('Received unexpected key press event for <%s> from push button monitor' % (keypress))

                        # ignore all other key presses
                        else:
                            pass

                    sleep(0.1)
                except Exception, e:
                    exType, ex, tb = sys.exc_info()
                    logger.critical("Exception occurred of type %s in push button monitor" % (exType.__name__))
                    logger.critical(str(e))
                    traceback.print_tb(tb)


# ------------------------------------------------------------------------------
class VibrationMotor(IVibrationMotor):
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 name,
                 outputPin):
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
        self.Name = name + " (" + outputPin +")"

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
        logger.debug('Entering vibration motor %s', self.Name)
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
        logger.debug('Exiting vibration motor %s', self.Name)
        self.stop()

    # --------------------------------------------------------------------------
    def start(self):
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
        logger.debug('Started vibration motor \"%s\".', self.Name)

    # --------------------------------------------------------------------------
    def stop(self):
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
        logger.debug('Stopped vibration motor \"%s\".', self.Name)

# ------------------------------------------------------------------------------
class Buzzer(IBuzzer):
    """
    The buzzer class enables a fake console buzzer to be play or stop a
    single note, or play a preconfigured song asynchronously.
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 name, 
                 config):
        """Initializes the Buzzer class

        TODO Detailed multi-line description if
        necessary.

        Args:
            name (string): Name of this instance of the Buzzer class. Example "Bob"
            config (Config): Conifg object containing an array named Song which is an
                             array of configuration objects with Tone and Duration.
                             Where Tone is an int from 0-TBD and Duration is a number
                             with the duration of time in seconds. 
        Returns:
            N/A
        Raises:
            N/A

        """
        self.Name = name
        logger.debug('Init buzzer \"%s\".' % self.Name)
        # Copy the song to play
        self._song = []
        self.TotalDuration = 0
        for i in config.Song:
           # TODO verify there is not just a copy constructor for config
           # TODO verify tone is an int and Duration is a number
           tmp = station.util.Config()

           isFile = False
           hasTrack = False
           # Depending on how used these might not be there
           if hasattr(i, 'File') and i.File != None:
               tmp.File = i.File
               isFile = True
           if hasattr(i, 'Track') and i.Track != None:
               tmp.Track = i.Track
               hasTrack = True
           if hasattr(i, 'Tone') and i.Tone != None:
               tmp.Tone = i.Tone
           if hasattr(i, 'Duration') and i.Duration != None:
               tmp.Duration = i.Duration
           self._song.append(tmp)

           if isFile and hasTrack:
              if os.path.isfile(i.File):
                 # this is likely a midi now things get hard
                 try:
                    logger.debug('Opening midi file \"%s\".' % i.File)
                    mid = MidiFile(i.File)
                    logger.debug('Opened midi file \"%s\".' % i.File)
                    # now find the track
                    for track in enumerate(mid.tracks):
                       if hasattr(track, 'name') and track.name == i.Track:
                          for message in track:
                             if message.type == 'note_on':
                                # need to force data type to avoid int division
                                duration = 0.0 + message.time
                             elif message.type == 'note_off':
                                duration = message.time - duration
                                if duration > 0:  
                                   self.TotalDuration += duration/1000.0
                 except Exception, e:
                    exType, ex, tb = sys.exc_info()
                    logger.critical("Exception occurred of type %s in Buzzer run" % (exType.__name__))
                    logger.critical(str(e))
                    traceback.print_tb(tb)
              else:
                 # The file does not exist
                 logger.critical("The buzzer %s file %s does not exist", self.Name, i.File)
           else:
              # duration is easy just add em up
              self.TotalDuration += i.Duration
        self._stopPlaying = True
        self._thread = Thread(target=self.run)
        #self._thread.daemon = True
        # Only start the thread to play the song when commanded.

    # --------------------------------------------------------------------------
    def __enter__(self):
        logger.debug('Entering Buzzer')
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
        logger.debug('Exiting Buzzer')
        self._stopPlaying = True
        self._thread.join()

    # --------------------------------------------------------------------------
    def play(self):
        """Asynchronously plays this Buzzer's song.

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
        logger.debug('Buzzer starting to play configured song')
        if not self._stopPlaying:
           # The song is already playing so need to restart it
           self.off(self)
        self._stopPlaying = False
        self._thread.start()

    # --------------------------------------------------------------------------
    def playSynchronously(self):
        """Synchronously plays this Buzzer's song.

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
        logger.debug('Buzzer starting to play configured song')
        if not self._stopPlaying:
           # The song is already playing so need to restart it
           self.off(self)
        self._stopPlaying = False
        self.run()

    # --------------------------------------------------------------------------
    def note(self,
             tone):
        """Has the buzzer hold a note unit off is called.

        So pibrella docs are light but looking at it's source code would suggest
        that the tone field is the standard midi value minus 69 so negative is
        allowed and 0-11 would be with higher or lower values just in different
        octaves:
        note_key = ['A','A#','B','C','C#','D','D#','E','F','F#','G','G#']

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
        logger.debug('Buzzer playing note %s' % tone)
        # TODO verify tone is an int

    # --------------------------------------------------------------------------
    def off(self):
        """Stops playing the buzzer's song or note.

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
        logger.debug('Stop playing Buzzer')
        if not self._stopPlaying:
           # Need to stop the song thread first
           self._stopPlaying = True
           self._thread.join()
        logger.debug('Buzzer turning off')

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

        for i in self._song:
           # first assess if this is a string of notes or a midi file
           if hasattr(i,'File'):
              # this is likely a midi
              try:
                 mid = MidiFile(i.File)
                 # now find the track
                 for track in enumerate(mid.tracks):
                    if track.name == i.Track:
                       for message in track:
                          if message.type == 'note_on':
                             note = message.note - 69
                             logger.debug('Buzzer playing note %s' % note)
                             # need to force data type to avoid int division
                             duration = 0.0 + message.time
                          elif message.type == 'note_off':
                             duration = message.time - duration
                             if duration > 0:
                                sleep(duration/1000.0)
                             logger.debug('Buzzer turning off')
                 logger.debug('Buzzer turning off')
              except Exception, e:
                 exType, ex, tb = sys.exc_info()
                 logger.critical("Exception occurred of type %s in Buzzer run" % (exType.__name__))
                 logger.critical(str(e))
                 traceback.print_tb(tb)
           else:
              try:  
                 if self._stopPlaying:
                    logger.debug('Buzzer turning off')
                    break
                 logger.debug('Buzzer playing note %s' % i.Tone)
                 sleep(i.Duration)
              except Exception, e:
                 exType, ex, tb = sys.exc_info()
                 logger.critical("Exception occurred of type %s in Buzzer run" % (exType.__name__))
                 logger.critical(str(e))
                 traceback.print_tb(tb)

        self._stopPlaying = True

# ------------------------------------------------------------------------------
class Input(IInput):
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 name,
                 inputPin):
        """TODO strictly one-line summary

        TODO Detailed multi-line description if
        necessary.

        Args:
            arg1 (type1): TODO describe arg, valid values, etc.
            name (string): Name of this input, example "lightDetector"
            inputPin (string): Letter Designation of Pin , "a", "b", "c", or"d"
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        self.Name = name
        self._inputValue = 0
        #self._inputPin = getattr(pibrella.input, inputPin)

    # --------------------------------------------------------------------------
    def read(self):
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
        #return self._inputPin.read()
        # TODO Mock input state using console keys
        return self._inputValue

# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

