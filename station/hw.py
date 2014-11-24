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

import logging
import logging.handlers
import pibrella
import signal
import sys
from threading import Thread
from time import sleep
import traceback

#from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
from interfaces import IDisplay
from interfaces import ILed
from interfaces import IPushButtonMonitor
from interfaces import IVibrationMotor
from interfaces import IBuzzer
from interfaces import IInput
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
        self._lcd = Adafruit_CharLCDPlate()

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
        self._lcd.begin(16, 2)
        self._lcd.clear()
        self._lcd.noCursor()
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
        self._lcd.stop()

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
        self._refreshDisplay()
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
        self._refreshDisplay()
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

        self._refreshDisplay()
        logger.debug('Setting Line 2 text. Display now reads "%s"[br]"%s"' %
                     (self._line1Text, self._line2Text))

    # --------------------------------------------------------------------------
    def _refreshDisplay(self):
        """TODO single-line comment

        TODO multi-line
        comment

        Args:
            N/A.
        Returns:
            N/A.
        Raises:
            N/A.

        """
        self.setText(self._line1Text + '\n' + self._line2Text)


# ------------------------------------------------------------------------------
class Led(ILed):
    """
    TODO class comment
    """

    # --------------------------------------------------------------------------
    def __init__(self,
                 name, 
                 config):
        """Initializes the LED class

        TODO Detailed multi-line description if
        necessary.

        Args:
            name (string): Name of this instance of the LED class. Example "Bob"
            config (Config): Configuration object for the LED class
        Returns:
            N/A
        Raises:
            N/A

        """
        self.Name = name
        self.FlashingOnDuration_s = 0.5
        self.FlashingOffDuration_s = 0.5
        self.outputPin = getattr(pibrella.light, config.OutputPin)

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
        logger.debug('Set LED steady ON \"%s\".', self.Name)
        self.outputPin.on()

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
        logger.debug('Set LED steady OFF \"%s\".', self.Name)
        self.outputPin.off()

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
        logger.debug('Set LED flashing \"%s (%s..%s)\".',
                     self.Name,
                     self.FlashingOnDuration_s,
                     self.FlashingOffDuration_s)
        
        # Pulse function, FadeInTime_s, FadeOutTime_s, OnTime_s, OffTime_s
        self.outputPin.pulse(0, 0, self.FlashingOnDuration_s, self.FlashingOffDuration_s);


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
        # TODO[BEGIN]
        keypress = config.HwKeyPress

        if keypress in self._pushButtons:
            logger.warning('Console key [%s] already registered to push button %s; redefining to register to push button %s' %
                           (keypress, self._pushButtons[keypress].Name, name))

        self._pushButtons[keypress] = PushButton(name, buttonPressHandler)

        logger.debug('Registered push button %s for key press [%s]' %
                     (name, keypress))
        # TODO[END]

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

                        # TODO
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
            name (string): Name of this motor, example "Huey"
            outputPin (string): Letter Designation of Pin , "E", "F", "G", or"H"
        Returns:
            TODO describe the return type and details
        Raises:
            TodoError1: if TODO.
            TodoError2: if TODO.

        """
        self.Name = name
        #TODO - Need to get these from config file [SS]
        #self.OnDuration_s = 0.5
        #self.OffDuration_s = 0.5
        self.outputPin = getattr(pibrella.output, outputPin)

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
        self.outputPin.on()

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
        self.outputPin.off()


# ------------------------------------------------------------------------------
class Buzzer(IBuzzer):
    """
    The buzzer class enables a pibrella buzzer to be play or stop a
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
                    logger.debug('Opening midi file \"%s\".' % (i.File))
                    mid = MidiFile(i.File)
                    logger.debug('Opened midi file \"%s\".' % (i.File))
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
        self._buzzer = getattr(pibrella, 'buzzer')
        self._stopPlaying = False
        self._thread = Thread(target=self.run)
        self._isWaitingForPlay = True
        self._isCutShort = False
        self._thread.start()

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
        self._isWaitingForPlay = True
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
        if (not self._stopPlaying) and (not self._isWaitingForPlay):
           # The song is already playing so need to restart it
           self.off(self)
        self._isWaitingForPlay = False

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
        if (not self._stopPlaying) and (not self._isWaitingForPlay):
           # The song is already playing so need to restart it
           self.off(self)
        self._isWaitingForPlay = True
        self._playOnce()

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
        if (not self._stopPlaying) and (not self._isWaitingForPlay):
           # The song is already playing so need to stop it
           self.off(self)
        self._buzzer.note(tone)

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
        if (not self._stopPlaying) and (not self._isWaitingForPlay):
            self._isCutShort = True
            while self._isCutShort:
                sleep(0.0001)
        self._buzzer.off()

    # --------------------------------------------------------------------------
    def _playOnce(self):
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
                 # now find the track to play
                 for track in mid.tracks:
                    if hasattr(track, 'name') and track.name == i.Track:
                       for message in track:
                          # if asynch give a way to stop
                          if self._stopPlaying or self._isCutShort:
                             self._buzzer.off()
                             self._isCutShort = False #reset for next run
                             break
                          if message.type == 'note_on':
                             note = message.note - 69
                             pibrella.buzzer.note(note)
                             # need to force data type to avoid int division
                             duration = 0.0 + message.time
                          elif message.type == 'note_off':
                             duration = message.time - duration
                             if duration > 0:
                                sleep(duration/1000.0)
                             pibrella.buzzer.off()
                 pibrella.buzzer.off()
              except Exception, e:
                 exType, ex, tb = sys.exc_info()
                 logger.critical("Exception occurred of type %s in Buzzer run" % (exType.__name__))
                 logger.critical(str(e))
                 traceback.print_tb(tb)
           else:
              try:  
                 # if asynch give a way to stop
                 if self._stopPlaying or self._isCutShort:
                    self._buzzer.off()
                    isCutShort = False #reset for next run
                    break
                 self._buzzer.note(i.Tone)
                 sleep(i.Duration)
                 self._buzzer.off()
              except Exception, e:
                 exType, ex, tb = sys.exc_info()
                 logger.critical("Exception occurred of type %s in Buzzer run" % (exType.__name__))
                 logger.critical(str(e))
                 traceback.print_tb(tb)
        # End for i

        self._isWaitingForPlay = True

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

        # Note doing it this way gets rid of issue of restarting a thread
        # if you need to stop short, but it chews up CPU
        # TODO there needs to be a better way of using a worker thread instead
        # of a self thread but still be able to signal the worker thread to stop
        # early without relying on a member variable.
        while not self._stopPlaying:
           if self._isWaitingForPlay:
               sleep(0.0001)
           else:
               self._playOnce()

# TODO use inheritance to deduplicate this class and the console.Buzzer class.
# ------------------------------------------------------------------------------
class SilentBuzzer(IBuzzer):
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

           # Depending on how used these might not be there
           if hasattr(i, 'File') and i.File != None:
               tmp.File = i.File 
           if hasattr(i, 'Track') and i.Track != None:
               tmp.Track = i.Track
           if hasattr(i, 'Tone') and i.Tone != None:
               tmp.Tone = i.Tone
           if hasattr(i, 'Duration') and i.Duration != None:
               tmp.Duration = i.Duration
           self._song.append(tmp)

           if hasattr(i, 'File') and i.File != None:
              if os.path.isfile(i.File):
                 # this is likely a midi now things get hard
                 try:
                    logger.debug('Opening midi file \"%s\".' % i.File)
                    mid = MidiFile(i.File)
                    logger.debug('Opened midi file \"%s\".' % i.File)
                    # now find the track
                    for track in mid.tracks:
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
        logger.debug('Entering SilentBuzzer')
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
        logger.debug('Exiting SilentBuzzer')
        self._stopPlaying = True
        self._thread.join()

    # --------------------------------------------------------------------------
    def play(self):
        """Asynchronously plays this SilentBuzzer's song.

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
        logger.debug('SilentBuzzer starting to play configured song')
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
        logger.debug('SilentBuzzer starting to play configured song')
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
        logger.debug('SilentBuzzer playing note %s' % tone)
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
        logger.debug('Stop playing SilentBuzzer')
        if not self._stopPlaying:
           # Need to stop the song thread first
           self._stopPlaying = True
           # TODO fix SilentBuzzer threading self._thread.join()
        logger.debug('SilentBuzzer turning off')

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
              if os.path.isfile(i.File):
                 # this is likely a midi
                 try:
                    mid = MidiFile(i.File)
                    # now find the track
                    for track in enumerate(mid.tracks):
                       if hasattr(track, 'name') and track.name == i.Track:
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
                                logger.debug('SilentBuzzer turning off')
                    logger.debug('Buzzer turning off')
                 except Exception, e:
                    exType, ex, tb = sys.exc_info()
                    logger.critical("Exception occurred of type %s in SilentBuzzer run" % (exType.__name__))
                    logger.critical(str(e))
                    traceback.print_tb(tb)
              else:
                 # The file does not exist
                 logger.critical("The SilentBuzzer %s file %s does not exist", self.Name, i.File)
           else:
              try:  
                 if self._stopPlaying:
                    logger.debug('SilentBuzzer turning off')
                    break
                 logger.debug('SilentBuzzer playing note %s' % i.Tone)
                 sleep(i.Duration)
              except Exception, e:
                 exType, ex, tb = sys.exc_info()
                 logger.critical("Exception occurred of type %s in SilentBuzzer run" % (exType.__name__))
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
        self._inputPin = getattr(pibrella.input, inputPin)

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
        return self._inputPin.read()

# ------------------------------------------------------------------------------
# Module Initialization
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO - delete
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

