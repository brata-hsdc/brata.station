from mido import MidiFile
from time import sleep
import pibrella

""" fade test
pibrella.light.red.fade(0,100,10)
sleep(11)
pibrella.light.red.fade(100,0,10)
sleep(11)
"""

""" start
pibrella.buzzer.note(-9)
sleep(.9)
pibrella.buzzer.off()
sleep(0.1)
pibrella.buzzer.note(-9)
sleep(0.9)
pibrella.buzzer.off()
sleep(0.1)
pibrella.buzzer.note(-9)
sleep(0.9)
pibrella.buzzer.off()
sleep(0.1)
pibrella.buzzer.note(3)
sleep(0.9)
pibrella.buzzer.off()
"""

""" fail
pibrella.buzzer.note(0)
sleep(1.25)
pibrella.buzzer.note(-7)
sleep(2)
pibrellay.buzzer.off()
"""

""" Mike notes for success likely bond theme
and need a calibration mode
push button yellow goes on then as turn the light can change untl the light changes
press red button again to go back to operational state

"""

""" it knows it is a comment """
mid = MidiFile('bond.mid')

for i, track in enumerate(mid.tracks):
   print('Track ')
   print(track.name)
   if track.name == '':
      for message in track:
         if message.type == 'note_on':
            # print('Turn on ')
            note = message.note - 69
            print(note)
            pibrella.buzzer.note(note)
            duration = 0.0 + message.time
         elif message.type == 'note_off':
            print(duration)
            duration = message.time - duration
            if duration > 0:
               sleep(duration/1000.0)
            pibrella.buzzer.off()
pibrella.buzzer.off()

