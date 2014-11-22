import pibrella, signal
import time

# Keep track of when the CPA starts
start_time = 0

# Keep track of if we have finished init and are running
running = False
correct_flash_detected = False

# Max time from start to see a completed flash or failed
MAX_TIME = 10

# Min time which must elapse before a flash start is detected
MIN_TIME = 9

# Time and duration to turn on green indicating to autofire
GO_TIME = 6
GO_DURATION = 0.1

def reportStatus(passed):
   global running
   # In either case reset
   running = False
   pibrella.output.h.off()
   pibrella.light.stop()
   if passed:
      print("Nailed It!")
      pibrella.light.pulse(0.2)
      pibrella.buzzer.success()
   else:
      print("Failed!")
      pibrella.buzzer.fail()

   # TBD report the failure or success to the server

   pibrella.light.stop()

def alarm(pin):
   global running, start_time, MIN_TIME, correct_flash_detected
   if running:
      if pin.read() == 1:
         # ensure this was the first and only flash
         if correct_flash_detected:
            # This should not happen unless they strobed
            print("No strobing!")
            reportStatus(False)
            exit()
         time_flash_started = time.time() - start_time
         if time_flash_started > MIN_TIME:
            correct_flash_detected = True
         else:
            # Flash was too early so call failed
            print("Flashed too soon!")
            print(time_flash_started)
            reportStatus(False)
      elif pin.read() == 0:
         if correct_flash_detected:
            # So we are seeing the falling edge of flash
            time_flash_ended = time.time() - start_time
            if time_flash_ended < MAX_TIME:
               reportStatus(True)
   # if we were not running then we do not care

def start(pin):
   global running, start_time, correct_flash_detected
   running = False
   correct_flash_detected = False
   pibrella.light.stop()
   pibrella.output.h.on()
   pibrella.light.red.on()
   pibrella.buzzer.note(0)
   time.sleep(1)
   pibrella.light.red.off()
   pibrella.light.yellow.on()
   pibrella.buzzer.note(1)
   time.sleep(1)
   pibrella.light.yellow.off()
   pibrella.light.green.on()
   pibrella.buzzer.note(2)
   start_time = time.time();
   running = True
   time.sleep(1)
   pibrella.light.green.off()
   pibrella.buzzer.off()

def waitingForFlash():
   global running, start_time, MAX_TIME, GO_TIME, GO_DURATION, correct_flash_detected
   # This loop is continuously called while waiting for
   # asynch input.  It is needed to be able to catch the
   # time out case.
   while running:
      elapsed_time = time.time() - start_time
      if elapsed_time > GO_TIME and elapsed_time < GO_TIME + GO_DURATION:
         # This should only happen once
         pibrella.light.green.on()
         time.sleep(FLASH_DURATION)
         pibrella.light.green.off()
      elif elapsed_time > MAX_TIME:
         if correct_flash_detected:
            print("Flash stayed on too long!")
         else:
            print("Flash started too Late!")
         print(elapsed_time)
         reportStatus(False)
      time.sleep(0.01)

pibrella.button.pressed(start)
pibrella.input.d.changed(alarm)

# TBD need a function that the server calls to start
start(pibrella.button)
pibrella.loop(waitingForFlash)
pibrella.pause()