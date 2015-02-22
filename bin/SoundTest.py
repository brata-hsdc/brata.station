#!/usr/bin/python

import sys
import time
import random

sys.path.append('/user/lib/python2.7/dist-packages')
import pygame

pygame.mixer.init()

def waitDone():
    while pygame.mixer.music.get_busy() == True:
        pass

def old_uh_oh():    
    pygame.mixer.music.load('wavTones.com.unregistred.sin_932.9Hz_-6dBFS_1.0s.wav')
    pygame.mixer.music.play()
    pygame.mixer.music.queue('wavTones.com.unregistred.sin_784.5Hz_-6dBFS_1.0s.wav')
    waitDone()


def old_countdown():
    pygame.mixer.init()
    pygame.mixer.music.load('wavTones.com.unregistred.sin_1000Hz_-6dBFS_0.5s.wav')
    pygame.mixer.music.play()

    waitDone()
    time.sleep(0.5)
    pygame.mixer.music.rewind()
    pygame.mixer.music.play()

    waitDone()
    time.sleep(0.5)
    pygame.mixer.music.rewind()
    pygame.mixer.music.play()

    waitDone()
    pygame.mixer.music.load('wavTones.com.unregistred.sin_2000Hz_-6dBFS_0.5s.wav')
    time.sleep(0.5)
    pygame.mixer.music.play()

    waitDone()

def countdown():
    pygame.mixer.music.load('countdown.wav')
    pygame.mixer.music.play()
    waitDone()

def uh_oh():
    pygame.mixer.music.load('uh_oh.wav')
    pygame.mixer.music.play()
    waitDone()
    
def playBond():
    pygame.mixer.music.load('/opt/designchallenge2015/brata.station/bin/bond_theme.wav')
    #pygame.mixer.set_volume(1.0)
    pygame.mixer.music.play()
    waitDone()

playBond()
#countdown()
#time.sleep(2.0)
#uh_oh()


