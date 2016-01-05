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

from collections import namedtuple
import sys
import os.path
import itertools
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
    
    DEFAULT_FONT = 'freesansbold.ttf'
    DEFAULT_FONT_SIZE = 100
    
    def __init__(self, pt, value="", size=DEFAULT_FONT_SIZE, font=DEFAULT_FONT, justify=LEFT|BOTTOM, color=Colors.WHITE, intervalsMs=(1000,0)):
        """ intervalMs is a list of (off, on, off, on, ...) time intervals used to toggle the text visibility """
        super(Text, self).__init__()
        
        self.pos = pt
        self.pointSize = size
        self.font = pygame.font.Font(font, self.pointSize)
        self.justify = justify
        self.color = color
        self.image = None # required by sprite.draw()
        self.intervalsMs = itertools.cycle(intervalsMs)  # create a cycle iterator
        self.toggleTimeMs = 0
        self.rect = None  # required by sprite.draw()
        self._value = None
        self.setValue(value)  # sets _value and image
        
        self.visible=0
        self.update()
        
    def value(self):
        return self._value
    
    def setValue(self, value, color=None):
        self._value = value
        if color:
            self.color = color
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
    
    def update(self):
        """ Determine the visibility, then draw """
        t = pygame.time.get_ticks()
        while t >= self.toggleTimeMs:
            self.visible = (self.visible + 1) % 2  # toggle between 0 and 1
            self.dirty = self.visible + 1  # set to 2 (always dirty) when visible
            self.toggleTimeMs = t + next(self.intervalsMs)
    
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
class ImgObj(pygame.sprite.DirtySprite):
    
    def __init__(self, path, canvas=None, alpha=False, pivot=(0,0)):
        # Call the parent class (Sprite) constructor
#         pygame.sprite.Sprite.__init__(self)
        super(ImgObj, self).__init__()
       
        # Load an image, creating a Surface.
        self.image = pygame.image.load(path)
#         self.canvas = canvas
#         if canvas:
        if alpha:
            self.image = self.image.convert_alpha()
        else:
            self.image = self.image.convert()
            
        self.pivot = pivot
        
        self.children = []  # Tethered children

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.eraseRect = self.rect.copy()
    
    def x(self): return self.rect.x
    def y(self): return self.rect.y
    def pos(self): return (self.x(), self.y())
    def pivotX(self): return self.rect.x + self.pivot[0]
    def pivotY(self): return self.rect.y + self.pivot[1]
    def pivotPos(self): return (self.pivotX(), self.pivotY())
    
    def lerp(self, st, en, p):
        return float(en - st) * p + float(st)
    
    def moveTo(self, p):
        """ Move to point (x,y) """
        self.rect.x = p[0] - self.pivot[0]
        self.rect.y = p[1] - self.pivot[1]
        
        if self.children:
            self.moveChildren()
    
    def moveChildren(self):
        for c in self.children:
            c.moveTo((0, 0))
    
    def moveBetween(self, p1, p2, frac):
        """ Linearly interpolate between p1 and p2.
            Move to a point linearly interpolated between point p1 and point p2.
            frac is the interpolation amount.
        """
        self.moveTo((self.lerp(p1[0], p2[0], frac), self.lerp(p1[1], p2[1], frac)))
    
    def addChild(self, tetheredChild):
        self.children.append(tetheredChild)

#----------------------------------------------------------------------------
class TetheredImgObj(ImgObj):
    """ An ImgObj that moves relative to a parent ImgObj. """
    
    def __init__(self, path, canvas=None, alpha=False, pivot=(0,0), parent=None, offset=(0,0)):
        super(TetheredImgObj, self).__init__(path, canvas=canvas, alpha=alpha, pivot=pivot)
        self.parent = parent
        self.parent.addChild(self)
        self.offset = offset
    
    def moveTo(self, dxy):
        """ Move to offset relative to parent specified by delta """
#         self.offset = dxy
        super(TetheredImgObj, self).moveTo((self.parent.pivotX() + self.offset[0], self.parent.pivotY() + self.offset[1]))
    
#----------------------------------------------------------------------------
class AnimGroup(pygame.sprite.LayeredDirty):
    """ A Group that can sequence through multi-image sprites.
        This creates an effect like an animated GIF.
        The group can handle multiple sequences.
    """

    def __init__(self):
        self.sequences = []  # list of sequences; each seq is a list [curr#, (sprite, sprite, ...)]
        super(AnimGroup, self).__init__()
#         pygame.sprite.RenderUpdates.__init__(self, [])
        
    
    def add(self, seq=None):
        """ Add an image sequence to the group.
            seq is a list or tuple of Sprites.
        """
        if seq:
            # Make all images invisible to start
            for s in seq:
                s.visible = 0
                
#             self.sequences.append([0, seq])
            self.sequences.append(itertools.cycle(seq))
            super(AnimGroup, self).add(*seq)
    
    def draw(self, surface):
        """ Activate the next image in each sequence and draw. """
        visibleSprites = []
        
        for s in self.sequences:
            sp = next(s)
            sp.visible = 1
            sp.dirty = 1
            visibleSprites.append(sp)
        
        rects = super(AnimGroup, self).draw(surface)
        
        for sp in visibleSprites:
            sp.visible = 0
        
        return rects

#----------------------------------------------------------------------------
class FlightProfileApp(object):
    """ The app reads and displays flight profile information from the Master Server.
        The app uses pygame to display sprite-based graphics.
    """
    WINDOW_TITLE = "Flight Profile"
    FULLSCREEN = True
    
    MAX_SIM_DURATION_S = 45.0  # longer sim will be compressed to 45 sec.
#     MAX_SIM_DURATION_S = 10.0  # longer sim will be compressed to 10 sec.
    
    BG_LAYER    = 0
    LABEL_LAYER = 1
    TEXT_LAYER  = 2
    SHIP_LAYER  = 3
    
    SCREEN_CENTER     = (960, 540)
    FLIGHT_PATH_START = (400, 600)
    FLIGHT_PATH_END   = (1600, 750)
    
    STARS_BG_IMG = "img/Star-field_2_cropped.jpg"
    STARS_BG_POS = (0, 0)
    
    EARTH_BG_IMG = "img/earth_cropped.png"
    EARTH_BG_POS = (0, 800)
    
    STATION_IMG   = "img/station_2.png"
    STATION_PIVOT = (16, 225)  # docking port
    STATION_POS   = FLIGHT_PATH_END
    
    CAPSULE_IMG   = "img/capsule_2.png"
    CAPSULE_PIVOT = (234, 98) # nose
    CAPSULE_POS   = FLIGHT_PATH_START
    
    FLAME_IMG     = ("img/flame-1.png", "img/flame-2.png", "img/flame-3.png", "img/flame-4.png")
    FLAME_PIVOT   = (198, 98) # base of flame
    FLAME_OFFSET  = (-200, 0)
    
    FLAME_UP_IMG    = ("img/small_flame_up-1.png", "img/small_flame_up-2.png", "img/small_flame_up-3.png", "img/small_flame_up-4.png")
    FLAME_UP_PIVOT  = (11, 86)
    FLAME_UP_OFFSET = (-24, -21)
    
    FLAME_DOWN_IMG    = ("img/small_flame_down-1.png", "img/small_flame_down-2.png", "img/small_flame_down-3.png", "img/small_flame_down-4.png")
    FLAME_DOWN_PIVOT  = (11, 16)
    FLAME_DOWN_OFFSET = (-24, 21)
    
    # An object to hold the flight profile parameters
    #   tAft    is the duration of the acceleration burn, in seconds
    #   tCoast  is the duration of the coast phase, in seconds
    #   tFore   is the duration of the deceleration burn, in seconds
    #   aAft    is the force of acceleration, in m/sec^2
    #   aFore   is the force of deceleration, in m/sec^2
    #   rFuel   is the rate of fuel consumption in kg/sec
    #   qFuel   is the initial amount of fuel, in kg
    #   dist    is the initial distance to the dock, in m
    FlightParams = namedtuple('FlightParams', 'tAft tCoast tFore aAft aFore rFuel qFuel dist')
    
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
        self.fullscreen = self.FULLSCREEN
        
        self.maxVelocity = 0.0
        self.simPhase = DockSim.START_PHASE
        self.outOfFuel = False
        
        self.staticGroup = pygame.sprite.LayeredUpdates()
        self.statsGroup  = pygame.sprite.LayeredDirty()
        self.blinkingTextGroup = pygame.sprite.LayeredDirty()
        self.movingGroup = pygame.sprite.OrderedUpdates()
        self.animGroup   = AnimGroup()

    def initPygame(self):
        """ Initialize the pygame modules that we need """
#         pygame.init()
        pygame.display.init()
        pygame.font.init()
        self.frameClock = pygame.time.Clock()
        
    def setupBackgroundDisplay(self):
        scriptDir = os.path.dirname(__file__)
        self.stars = ImgObj(os.path.join(scriptDir, self.STARS_BG_IMG), alpha=False)
        self.stars.moveTo(self.STARS_BG_POS)
        
        self.earth = ImgObj(os.path.join(scriptDir, self.EARTH_BG_IMG), alpha=True)
        self.earth.moveTo(self.EARTH_BG_POS)
        
        self.staticGroup.add((self.stars, self.earth), layer=self.BG_LAYER)
    
    def setupMissionTimeDisplay(self):
        X = 100
        Y = 100
        LINE_SPACE = 70
        BIG_TEXT = 80
        SMALL_TEXT = 60
        TINY_TEXT = 35
        TAB1 = 300
        TAB2 = TAB1 + 40
        
        self.missionTimeLabel = Text((X, Y), value="Mission Time", size=BIG_TEXT)
        self.simulatedLabel   = Text((X+TAB1, Y+LINE_SPACE), value="Simulated:", size=SMALL_TEXT, justify=Text.RIGHT|Text.BOTTOM)
        self.actualLabel      = Text((X+TAB1, Y+LINE_SPACE*2), value="Actual:", size=SMALL_TEXT, justify=Text.RIGHT|Text.BOTTOM)
        self.compressionLabel = Text((X+TAB1, int(Y+LINE_SPACE*2.7)), value="Time Compression:", size=TINY_TEXT, justify=Text.RIGHT|Text.BOTTOM)
        self.staticGroup.add((self.missionTimeLabel, self.simulatedLabel, self.actualLabel, self.compressionLabel), layer=self.LABEL_LAYER)
        
        self.simulatedTime    = Clock((X+TAB2, Y+LINE_SPACE), size=SMALL_TEXT)
        self.actualTime       = Clock((X+TAB2, Y+LINE_SPACE*2), size=SMALL_TEXT)
        self.compression      = Text((X+TAB2, int(Y+LINE_SPACE*2.7)), value="{:0.1f}x".format(self.missionTimeScale), size=TINY_TEXT)
        self.statsGroup.add((self.simulatedTime, self.actualTime))
        self.staticGroup.add((self.compression), layer=self.LABEL_LAYER)
    
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
        self.vmaxLabel   = Text((X+TAB1, Y + LINE_SPACE*3), value="Max Rel Velocity:", size=SMALL_TEXT, justify=Text.RIGHT|Text.BOTTOM)
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
        
        # Load animated flames
        self.capsule = ImgObj(os.path.join(scriptDir, self.CAPSULE_IMG), alpha=True, pivot=self.CAPSULE_PIVOT)
        self.capsule.moveTo(self.CAPSULE_POS)
        
        self.rearFlame = [TetheredImgObj(os.path.join(scriptDir, f), alpha=True, pivot=self.FLAME_PIVOT, parent=self.capsule, offset=self.FLAME_OFFSET) for f in self.FLAME_IMG]
        self.frontFlameUp = [TetheredImgObj(os.path.join(scriptDir, f), alpha=True, pivot=self.FLAME_UP_PIVOT, parent=self.capsule, offset=self.FLAME_UP_OFFSET) for f in self.FLAME_UP_IMG]
        self.frontFlameDown = [TetheredImgObj(os.path.join(scriptDir, f), alpha=True, pivot=self.FLAME_DOWN_PIVOT, parent=self.capsule, offset=self.FLAME_DOWN_OFFSET) for f in self.FLAME_DOWN_IMG]
        
        self.station = ImgObj(os.path.join(scriptDir, self.STATION_IMG), alpha=True, pivot=self.STATION_PIVOT)
        self.station.moveTo(self.STATION_POS)
        
        self.movingGroup.add((self.station, self.capsule))
        
    def setupDisplay(self):
        """ Create the display window and the components within it """
        # Create the window
        if self.fullscreen:
            self.canvas = pygame.display.set_mode((0,1080), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)# | pygame.OPENGL)
        else:
            self.canvas = pygame.display.set_mode((0,1080), pygame.DOUBLEBUF | pygame.HWSURFACE)# | pygame.OPENGL)
#         self.canvas = pygame.display.set_mode((0,1080), pygame.FULLSCREEN | pygame.HWSURFACE)# | pygame.OPENGL)
        pygame.display.set_caption(self.WINDOW_TITLE)
        
        # Set up parts of the display
        self.setupBackgroundDisplay()
        self.setupMissionTimeDisplay()
        self.setupStatsDisplay()
        self.setupSpaceshipDisplay()
        
        self.timer = Timer()
        self.timer.start()
        
    def setFlightProfile(self, flightParams=None):
        # Get flight profile parameters
        if flightParams:
            self.profile = flightParams
        else:
            # Set to some default params for testing
            self.profile = self.FlightParams(
                                             tAft=8.2,#8.4#8.3
                                             tCoast=1, #0
                                             tFore=13.1,
                                             aAft=0.15,
                                             aFore=0.09,
                                             rFuel=0.7,
                                             qFuel=20,
                                             dist=15.0,
                                            )
        
        # Create a simulation object initialized with the flight profile
        self.dockSim = DockSim(self.profile)
        
        self.maxVelocity = 0.0
        
        # Get the total time of flight
        self.duration = self.dockSim.flightDuration()
        if self.duration is None:  # flight did not complete (0 or neg. velocity)
            self.duration = DockSim.MAX_FLIGHT_DURATION_S
        print("duration:", self.duration)
        
        self.simDuration = min(self.duration, self.MAX_SIM_DURATION_S)
        print("simDuration:", self.simDuration)
        
        self.missionTimeScale = max(1.0, float(self.duration)/self.MAX_SIM_DURATION_S)
        print("missionTimeScale:", self.missionTimeScale)
        print("terminalVelocity:", self.dockSim.terminalVelocity())
        print("success:", self.dockSim.dockIsSuccessful())
#         print("profile:", self.profile)
#         print("")
    
        self.simPhase = DockSim.START_PHASE  # set phase to initial simulation phase
        self.outOfFuel = False
    
    def createPassFailText(self, passed=True):
        GIANT_TEXT = 300
        text = Text(self.SCREEN_CENTER,
                    value="SUCCESS!" if passed else "FAIL!",
                    size=GIANT_TEXT,
                    color=Colors.GREEN if passed else Colors.RED,
                    justify=Text.CENTER|Text.MIDDLE,
                    intervalsMs=(1000,250))
        self.blinkingTextGroup.add(text)
        
    def drawCharts(self):
        pass
    
    def draw(self):
        # Draw background and labels (should only do when necessary)
        rectList = self.staticGroup.draw(self.canvas)
        
        # Draw changing text fields
        rectList += self.statsGroup.draw(self.canvas)
        
        # Draw graphical objects (capsule and station)
        rectList += self.animGroup.draw(self.canvas)
        rectList += self.movingGroup.draw(self.canvas)
        rectList += self.blinkingTextGroup.draw(self.canvas)
        
        # Only copy the modified parts of the canvas to the display
        pygame.display.update(rectList)
        
    def update(self):
        """ Update the simulation """
        # Update time
        t = self.timer.elapsedSec()
        self.simulatedTime.setValue(t)
        self.actualTime.setValue(t * self.missionTimeScale)
        
        # Update stats
        state = self.dockSim.shipState(t * self.missionTimeScale)
        
        if state.phase == DockSim.END_PHASE:
            self.timer.stop()
        
        self.maxVelocity = max(self.maxVelocity, state.currVelocity)
        self.distance.setValue("{:0.2f} m".format(self.profile.dist - state.distTraveled))
        self.velocity.setValue("{:0.2f} m/sec".format(state.currVelocity), color=Colors.GREEN if self.dockSim.safeDockingVelocity(state.currVelocity) else Colors.RED)
        self.vmax.setValue("{:0.2f} m/sec".format(self.maxVelocity))
        self.acceleration.setValue("{:0.2f} m/sec^2".format((0.0,
                                                             self.profile.aAft if not self.outOfFuel else 0.0,
                                                             0.0,
                                                             -self.profile.aFore if not self.outOfFuel else 0.0,
                                                             0.0,
                                                             0.0)[state.phase]))
        self.fuelRemaining.setValue("{:0.2f} kg".format(state.fuelRemaining), color=Colors.WHITE if state.fuelRemaining > 0.0 else Colors.RED)
        self.phase.setValue(DockSim.PHASE_STR[state.phase])
        
        # Update graphics
        changeDetected = False
        
        # Detect running out of fuel
        if not self.outOfFuel and state.fuelRemaining <= 0.0:
            self.outOfFuel = True
            changeDetected = True
            
        # Detect a phase change
        if state.phase != self.simPhase:
            self.simPhase = state.phase
            changeDetected = True
        
        if changeDetected:
            if state.phase == DockSim.ACCEL_PHASE:
                self.animGroup.empty()
                if not self.outOfFuel:
                    self.animGroup.add(self.rearFlame)
            elif state.phase == DockSim.DECEL_PHASE:
                self.animGroup.empty()
                if not self.outOfFuel:
                    self.animGroup.add(self.frontFlameUp)
                    self.animGroup.add(self.frontFlameDown)
            elif state.phase == DockSim.END_PHASE:
                self.animGroup.empty()
                self.createPassFailText(passed=self.dockSim.dockIsSuccessful())
            else:
                self.animGroup.empty()
        
        frac = state.distTraveled/self.profile.dist
        self.capsule.moveBetween(self.FLIGHT_PATH_START, self.FLIGHT_PATH_END, frac)
        
        for sp in self.blinkingTextGroup.sprites():
            sp.update()
        
    def mainLoop(self):
        """ Receive events from the user and/or application objects, and update the display """
        highPriorityEvents = []
        
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

    def run(self, flightProfile):
        self.setFlightProfile(flightProfile)
        self.initPygame()
        self.setupDisplay()
        self.mainLoop()
        
#============================================================================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-f", "--fullscreen", action="store_true", help="display graphics in 1920x1080 fullscreen mode")
    parser.add_argument("--tAft",   type=float, required=True, help="duration of acceleration burn phase, in sec")
    parser.add_argument("--tCoast", type=float, required=True, help="duration of coast phase, in sec")
    parser.add_argument("--tFore",  type=float, required=True, help="duration of deceleration burn phase, in sec")
    parser.add_argument("--aAft",   type=float, required=True, help="acceleration force, in m/sec^2")
    parser.add_argument("--aFore",  type=float, required=True, help="deceleration force, in m/sec^2")
    parser.add_argument("--rFuel",  type=float, required=True, help="rate of fuel consumption, in kg/sec")
    parser.add_argument("--qFuel",  type=float, required=True, help="initial fuel amount, in kg")
    parser.add_argument("--dist",   type=float, required=True, help="initial dock distance, in m")
    args = parser.parse_args()

    flightProfile = FlightProfileApp.FlightParams(tAft=args.tAft,
                                                  tCoast=args.tCoast,
                                                  tFore=args.tFore,
                                                  aAft=args.aAft,
                                                  aFore=args.aFore,
                                                  rFuel=args.rFuel,
                                                  qFuel=args.qFuel,
                                                  dist=args.dist,
                                                 )
    app = FlightProfileApp()
    app.fullscreen = args.fullscreen
    app.run(flightProfile)
    sys.exit(0)
