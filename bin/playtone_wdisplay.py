#!/usr/bin/python

import sys
import time
import random
import math
import numpy
import pibrella

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import Image
import ImageDraw
import ImageFont
import sys

sys.path.append('/user/lib/python2.7/dist-packages')
import pygame

def parse_secure_error(argument):
    switcher = {
        0: "      ",
        1: "Timeout",
        2: "Short pulse width",
        4: "Long pulse width",
        8: ">Bits or <stop gap",
        16: "Long stop gap"
        
    }
    return switcher.get(argument, "nothing")

def generate_sound(freq):

    #setup our numpy array to handle 16 bit ints, which is what we set our mixer to expect with "bits" up above
    buf = numpy.zeros((n_samples, 2), dtype = numpy.int16)
    max_sample = 2**(bits - 1) - 1

    t = numpy.arange(n_samples)/float(sample_rate )
    buf[:,0] = max_sample*numpy.sin(2*numpy.pi*freq*t)
    buf[:,1] = buf[:,0]
    return pygame.sndarray.make_sound(buf)

def button_pressed(pin):
    change_tones()

def change_tones():
    global tone
    global slist
    global tone_order

    slist[(tone_order[tone]+1)].stop() # stop the current tone
    tone = tone + 1
    if tone == (len(tone_order)): # go back to the beginning
        tone = 0
    slist[(tone_order[tone]+1)].play(loops = -1)
    print "Tone ID = ", (tone_order[tone])
    print "Tone = ", tone
    print "length = ", len(tone_order)
    display_message(parse_secure_error(0), disp_msg[tone])

def display_message(Line1, Line2):
    # First define some constants to allow easy resizing of shapes.
    # Write two lines of text.
    global disp
    global draw
    global padding
    global font_top
    global font_bot
    global width
    global height

    draw.rectangle((0,0,width,height), outline=0, fill=0)
    x = padding
    draw.text((x, top),    Line1,  font=font_top, fill=255)
    draw.text((x, top+14), Line2,  font=font_bot, fill=255)

    # Display image.
    disp.clear()
    disp.display()
    disp.image(image)
    disp.display()



# Raspberry Pi pin configuration:
RST = 22

# INPUTS
disp_msg = ["Tone #0",
            "Tone #1",
            "Tone #2",
            "Tone #3",
            "Tone #4",
            "Tone #5",
            "Tone #6",
            "Tone #7",
            "Tone #8",
            "Tone #9"]

# LOCALS
# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)    

bits        = 16       # audio resolution
duration    = 10       # Length of audio playback
sample_rate = 44100    # sample rate
tone        = 0        # start out in tone 0 (off)

# frequencies of tones
f = [44100, 276, 308, 340, 372, 404, 436, 468, 500]
#f = [44100, 1200, 2400, 340, 372, 404, 436, 468, 500]

# challenge tone IDs from MS
#tone_ID = [3, 5, 6, 2, 2, 3, 2, 0, 5]
tone_ID = [0, 1, 2, 3, 4, 5, 6, 7, 8]
print "Challenge tone IDs = ", tone_ID

tone_order = tone_ID
# add the zero frequency (off) to the order list
tone_order.insert(0, -1)
print "Challenge tone IDs for list = ", tone_order

n_samples = int(round(duration*sample_rate)) # number of samples
#n_samples = 40000
pygame.mixer.pre_init(44100, -bits, 2, 1024)
pygame.init()

#initialize the tones
slist = [generate_sound(f[count]) for count in range(len(f))]
slist[tone].play(loops = -1)

# This section will go in the init for the module
# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
padding = 2
top = padding
bottom = height-padding
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
font_name = '/usr/share/fonts/truetype/freefont/FreeMono.ttf'
font_top = ImageFont.truetype(font_name, 12)
font_bot = ImageFont.truetype(font_name, 20)
display_message(parse_secure_error(0), disp_msg[tone])


#This will keep the sound playing forever, the quit event handling allows the pygame window to close without crashing
pibrella.button.pressed(button_pressed)
_running = True
while _running:
	time.sleep(0.1)

pygame.quit()
