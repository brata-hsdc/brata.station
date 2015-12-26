#!/usr/bin/python
#
#   File: FlightProfile.py
# Author: Ellery Chan
#  Email: ellery@precisionlightworks.com
#   Date: 7 Dec 2015
"""
Display the flight profile of a team's docking attempt.
"""
from __future__ import print_function, division

import sys
import os.path
import pygame.sprite
import pygame.image
import pygame.font
import pygame.time

from DockSim import DockSim

#----------------------------------------------------------------------------
class Colors(object):
    WHITE   = (255, 255, 255)
    BLACK   = (  0,   0,   0)
    GREEN   = (  0, 255,   0)
    BLUE    = (  0,   0, 255)
    RED     = (255,   0,   0)
    YELLOW  = (255, 255,   0)
    CYAN    = (  0, 255, 255)
    MAGENTA = (255,   0, 255)

#----------------------------------------------------------------------------
class Text(pygame.sprite.DirtySprite):
    """ A displayable text object """
    
    LEFT   = 0x01
    CENTER = 0x02
    RIGHT  = 0x04
    BOTTOM = 0x10
    MIDDLE = 0x20
    TOP    = 0x40
    
    def __init__(self, pt, value="", size=100, font='freesansbold.ttf', justify=LEFT|BOTTOM, color=Colors.WHITE):
        super(Text, self).__init__()
        self.pos = pt
        self.pointSize = size
        self.font = pygame.font.Font(font, self.pointSize)
        self.justify = justify
        self.color = color
        self.image = None # required by sprite.draw()
        self.rect = None  # required by sprite.draw()
        self._value = None
        self.setValue(value)  # sets _value and image
        
    def value(self):
        return self._value
    
    def setValue(self, value):
        self._value = value
        self.image = self.font.render(self._value, True, self.color)
        self.dirty = 1

        self.rect = self.image.get_rect()
#         self.eraseRect = self.rect.copy()
        
        if self.justify & self.LEFT:
            self.rect.left = self.pos[0]
        elif self.justify & self.CENTER:
            self.rect.centerx = self.pos[0]
        else: # self.RIGHT
            self.rect.right = self.pos[0]
    
        if self.justify & self.BOTTOM:
            self.rect.bottom = self.pos[1]
        elif self.justify & self.CENTER:
            self.rect.centery = self.pos[1]
        else: # self.TOP
            self.rect.top = self.pos[1]
    
#----------------------------------------------------------------------------
class Timer(object):
    """ A timer object.  Computes elapsed time.
        Optionally generates a USEREVENT every tick.
        You set the tick interval in tickMs.
    """
     
    def __init__(self, periodMs=44, generateEvents=False):
        self.startTimeMs = 0
        self.stopTimeMs  = 0
        self.periodMs    = periodMs  # time between timer events
        self.generateEvents = generateEvents
    
    def isRunning(self):
        return self.stopTimeMs < self.startTimeMs
    
    def currentTime(self):
        """ Return the actual simulation time if the clock is running.
            If the clock has been stopped (by calling stop()), return
            the time when stop was called.
        """
        if self.isRunning():
            return pygame.time.get_ticks()
        else:
            return self.stopTimeMs
 
    def start(self):
        """ Start the timer, and generate USEREVENTs """
        self.stopTimeMs = 0
        self.startTimeMs = pygame.time.get_ticks()
         
        # Generate a USEREVENT every periodMs milliseconds
        if self.generateEvents:
            pygame.time.set_timer(pygame.USEREVENT, self.periodMs)
     
    def stop(self):
        """ Stop the timer, and stop generating USEREVENTs """
        if self.isRunning():
            self.stopTimeMs = pygame.time.get_ticks()
            if self.generateEvents:
                pygame.time.set_timer(pygame.USEREVENT, 0)
         
    def elapsedMs(self):
        """ Return the elapsed time in milliseconds """
        return self.currentTime() - self.startTimeMs
     
    def elapsedSec(self):
        """ Return the elapsed time in seconds """
        return self.elapsedMs()/1000.0
    
#----------------------------------------------------------------------------
class Clock(Text):
    """ An Text object that knows how to format a time value """
    def __init__(self, pt, value=0, size=100, justify=Text.BOTTOM|Text.LEFT, **kwargs):
#         self.startTimeMs = 0
        super(Clock, self).__init__(pt, value=value, size=size, justify=justify, **kwargs)
    
    def setValue(self, value=None):
        """ Set the value of the clock in seconds
        """
        tSeconds = float(value)
        super(Clock, self).setValue("{:02d}:{:02d}:{:02d}".format(int(tSeconds//60), int(tSeconds%60), int((tSeconds%1) * 100)))
        
#----------------------------------------------------------------------------
class ImgObj(pygame.sprite.Sprite):
    
    def __init__(self, path, canvas=None, alpha=False):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
       
        # Load an image, creating a Surface.
        self.image = pygame.image.load(path)
#         self.canvas = canvas
#         if canvas:
        if alpha:
            self.image = self.image.convert_alpha()
        else:
            self.image = self.image.convert()

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.eraseRect = self.rect.copy()
    
    def x(self): return self.rect.x
    def y(self): return self.rect.y
    def pos(self): return (self.x(), self.y())
    
    def lerp(self, st, en, p):
        return float(en - st) * p + float(st)
    
    def moveTo(self, p):
        """ Move to point (x,y) """
        self.rect.x = p[0]
        self.rect.y = p[1]
    
    def moveBetween(self, p1, p2, frac):
        """ Linearly interpolate between p1 and p2.
            Move to a point linearly interpolated between point p1 and point p2.
            frac is the interpolation amount.
        """
        self.moveTo((self.lerp(p1[0], p2[0], frac), self.lerp(p1[1], p2[1], frac)))
        

#----------------------------------------------------------------------------
class FlightProfileApp(object):
    """ The app reads and displays flight profile information from the Master Server.
        The app uses pygame to display sprite-based graphics and matplotlib to display
        plots of the numerical flight profile data.
    """
    WINDOW_TITLE = "Flight Profile"
    
    MAX_SIM_DURATION_S = 45.0  # sim will not run for more than 45 sec.
    
    BG_LAYER = 0
    LABEL_LAYER = 1
    TEXT_LAYER = 2
    SHIP_LAYER = 3
    
    STARS_BG_POS = (0, 0)
    EARTH_BG_POS = (0, 800)
    STATION_POS  = (1000, 550)
    CAPSULE_POS  = (1, 600)
    
    class FlightParams(object):
        """ An object to hold the flight profile parameters """
        pass
    
    def __init__(self):
        self.canvas = None
        self.timer = None
        self.capsule = None
        self.station = None
        self.missionTimeLabel = None
        self.simulatedLabel = None
        self.actualLabel = None
        self.simulatedTime = None
        self.actualTime = None
        self.paramsLabel = None
        self.distLabel1 = None
        self.distLabel2 = None
        self.dist = None
        self.frameRate = 30 # fps
        self.frameClock = None
        
        self.staticGroup = pygame.sprite.LayeredUpdates()
        self.statsGroup  = pygame.sprite.RenderUpdates()
        self.movingGroup = pygame.sprite.OrderedUpdates()

    def initPygame(self):
        """ Initialize the pygame modules that we need """
#         pygame.init()
        pygame.display.init()
        pygame.font.init()
        self.frameClock = pygame.time.Clock()
        
    def setupBackgroundDisplay(self):
        scriptDir = os.path.dirname(__file__)
        self.stars = ImgObj(os.path.join(scriptDir, "img/Star-field_cropped.jpg"), alpha=False)
        self.stars.moveTo(self.STARS_BG_POS)
        
        self.earth = ImgObj(os.path.join(scriptDir, "img/earth_cropped.png"), alpha=True)
        self.earth.moveTo(self.EARTH_BG_POS)
        
        self.staticGroup.add((self.stars, self.earth), layer=self.BG_LAYER)
    
    def setupMissionTimeDisplay(self):
        X = 100
        Y = 100
        LINE_SPACE = 70
        BIG_TEXT = 80
        SMALL_TEXT = 60
        TAB1 = 300
        TAB2 = TAB1 + 40
        
        self.missionTimeLabel = Text((X, Y), value="Mission Time", size=BIG_TEXT)
        self.simulatedLabel   = Text((X+TAB1, Y+LINE_SPACE), value="Simulated:", size=SMALL_TEXT, justify=Text.RIGHT|Text.BOTTOM)
        self.actualLabel      = Text((X+TAB1, Y+LINE_SPACE*2), value="Actual:", size=SMALL_TEXT, justify=Text.RIGHT|Text.BOTTOM)
        self.staticGroup.add((self.missionTimeLabel, self.simulatedLabel, self.actualLabel), layer=self.LABEL_LAYER)
        
        self.simulatedTime    = Clock((X+TAB2, Y+LINE_SPACE), size=SMALL_TEXT)
        self.actualTime       = Clock((X+TAB2, Y+LINE_SPACE*2), size=SMALL_TEXT, color=Colors.RED)
        self.statsGroup.add((self.simulatedTime, self.actualTime))
    
    def setupStatsDisplay(self):
        X = 900
        Y = 100
        LINE_SPACE = 60
        BIG_TEXT = 80
        SMALL_TEXT = 50
        TAB1 = 450
        TAB2 = TAB1 + 40
        
        self.paramsLabel = Text((X, Y), value="Flight Profile Parameters", size=BIG_TEXT)
        self.distLabel   = Text((X+TAB1, Y + LINE_SPACE), value="Closing Distance:", size=SMALL_TEXT, justify=Text.RIGHT|Text.BOTTOM)
        self.velLabel    = Text((X+TAB1, Y + LINE_SPACE*2), value="Relative Velocity:", size=SMALL_TEXT, justify=Text.RIGHT|Text.BOTTOM)
        self.vmaxLabel   = Text((X+TAB1, Y + LINE_SPACE*3), value="Vmax:", size=SMALL_TEXT, justify=Text.RIGHT|Text.BOTTOM)
        self.accelLabel  = Text((X+TAB1, Y + LINE_SPACE*4), value="Acceleration:", size=SMALL_TEXT, justify=Text.RIGHT|Text.BOTTOM)
        self.fuelLabel   = Text((X+TAB1, Y + LINE_SPACE*5), value="Fuel Remaining:", size=SMALL_TEXT, justify=Text.RIGHT|Text.BOTTOM)
        self.phaseLabel  = Text((X+TAB1, Y + LINE_SPACE*6), value="Phase:", size=SMALL_TEXT, justify=Text.RIGHT|Text.BOTTOM)
        self.staticGroup.add((self.paramsLabel, self.distLabel, self.velLabel, self.vmaxLabel, self.accelLabel, self.fuelLabel, self.phaseLabel), layer=self.LABEL_LAYER)
        
        self.distance      = Text((X+TAB2, Y + LINE_SPACE), value="0", size=SMALL_TEXT)
        self.velocity      = Text((X+TAB2, Y + LINE_SPACE*2), value="0", size=SMALL_TEXT)
        self.vmax          = Text((X+TAB2, Y + LINE_SPACE*3), value="0", size=SMALL_TEXT)
        self.acceleration  = Text((X+TAB2, Y + LINE_SPACE*4), value="0", size=SMALL_TEXT)
        self.fuelRemaining = Text((X+TAB2, Y + LINE_SPACE*5), value="0", size=SMALL_TEXT)
        self.phase         = Text((X+TAB2, Y + LINE_SPACE*6), value="ACCELERATION", size=SMALL_TEXT)
        self.statsGroup.add((self.distance, self.velocity, self.vmax, self.acceleration, self.fuelRemaining, self.phase))
        
    def setupSpaceshipDisplay(self):
        scriptDir = os.path.dirname(__file__)
        self.capsule = ImgObj(os.path.join(scriptDir, "img/capsule.png"), alpha=True)
        self.capsule.moveTo(self.CAPSULE_POS)
        
        self.station = ImgObj(os.path.join(scriptDir, "img/station.png"), alpha=True)
        self.station.moveTo(self.STATION_POS)
        
        self.movingGroup.add((self.station, self.capsule))
        
    def setupDisplay(self):
        """ Create the display window and the components within it """
        # Create the window
        self.canvas = pygame.display.set_mode((0,1080), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)# | pygame.OPENGL)
#         self.canvas = pygame.display.set_mode((0,1080), pygame.FULLSCREEN | pygame.HWSURFACE)# | pygame.OPENGL)
        pygame.display.set_caption(self.WINDOW_TITLE)
        
        # Set up parts of the display
        self.setupBackgroundDisplay()
        self.setupMissionTimeDisplay()
        self.setupStatsDisplay()
        self.setupSpaceshipDisplay()
        
        
        self.timer = Timer()
        self.timer.start()
#         self.clock.start()
        
    def readFlightProfile(self):
        # Get flight profile parameters
        p = self.profile = self.FlightParams()
        p.tAft   = 8.2
        p.tCoast = 0
        p.tFore  = 13.1
        p.aAft   = 0.15
        p.aFore  = 0.09
        p.rFuel  = 0.7
        p.qFuel  = 20
        p.dist   = 15.0
        
        # Create a simulation object initialized with the flight profile
        self.dockSim = DockSim(p.tAft, p.tCoast, p.tFore, p.aAft, p.aFore, p.rFuel, p.qFuel, p.dist)
        
        self.profile.coastVel = self.dockSim.coastVelocity()
        self.profile.glideVel = self.dockSim.terminalVelocity()
        self.profile.maxVelocity = 0.0
        
        # Get the total time of flight
        self.duration = self.dockSim.flightDuration()
        if self.duration is None:  # flight did not complete (0 or neg. velocity)
            self.duration = DockSim.MAX_FLIGHT_DURATION_S
        
        self.simDuration = min(self.duration, self.MAX_SIM_DURATION_S)
        
        self.missionTimeScale = self.duration/self.MAX_SIM_DURATION_S
        if self.missionTimeScale < 1.0:
            self.missionTimeScale = 1.0
    
    def drawCharts(self):
        pass
    
    def draw(self):
        # Draw background and labels (should only do when necessary)
        self.staticGroup.draw(self.canvas)
        
        # Draw changing text fields
        rectList = self.statsGroup.draw(self.canvas)
        
        # Draw graphical objects (capsule and station)
        rectList += self.movingGroup.draw(self.canvas)
        
        # Only copy the modified parts of the canvas to the display
        pygame.display.update(rectList)
        
    def update(self):
        """ Update the simulation """
        # Update time
        if self.timer.elapsedSec() >= self.simDuration:
            self.timer.stop()
        t = self.timer.elapsedSec()
        self.simulatedTime.setValue(t)
        self.actualTime.setValue(t * self.missionTimeScale)
        
        # Update stats
        state = self.dockSim.shipState(t)
        
        self.profile.maxVelocity = max(self.profile.maxVelocity, state.currVelocity)
        self.distance.setValue("{:0.2f} m".format(self.profile.dist - state.distTraveled))
        self.velocity.setValue("{:0.2f} m/sec".format(state.currVelocity))
        self.vmax.setValue("{:0.2f} m/sec".format(self.profile.maxVelocity))
        self.acceleration.setValue("{:0.2f} m/sec".format((0, self.profile.aAft, self.profile.coastVel, self.profile.aFore, self.profile.glideVel)[state.phase]))
        self.fuelRemaining.setValue("{:0.2f}".format(state.fuelRemaining))
        self.phase.setValue(DockSim.PHASE_STR[state.phase])
        
        # Update graphics
        frac = state.distTraveled/self.profile.dist
#         self.capsule.moveBetween((1, 600), (1000, 600), self.timer.elapsedSec()/self.simDuration)
        self.capsule.moveBetween((1, 600), (1000, 600), frac)
        
    def mainLoop(self):
        """ Receive events from the user and/or application objects, and update the display """
        highPriorityEvents = []
#         lowPriorityEvents = []
#         timerEvents = []
        
        lastFrameMs = 0
        
        # Draw the whole background once
#         self.draw()
        self.staticGroup.draw(self.canvas)
        pygame.display.update()
        
        while True: # main game loop
            
            # Retrieve queued events from mouse, keyboard, timers
            highPriorityEvents += pygame.event.get(pygame.QUIT) +\
                                  pygame.event.get(pygame.KEYUP)
            pygame.event.get()  # flush the rest of the events
            
            # Retrieve an event from the event queue
            if highPriorityEvents:
                # Process the event
                #   First check to see whether we should quit
                event = highPriorityEvents.pop()
                if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    return
                
            # Refresh the display
            self.update()
            self.draw()
            lastFrameMs = self.frameClock.tick(self.frameRate)

    def run(self):
        self.initPygame()
        self.setupDisplay()
        self.readFlightProfile()
        self.mainLoop()
        
#============================================================================
if __name__ == "__main__":
    app = FlightProfileApp()
    app.run()
    sys.exit(0)
