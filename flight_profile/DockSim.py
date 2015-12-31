#!/usr/bin/python
#
#   File: DockSim.py
# Author: Ellery Chan
#  Email: ellery@precisionlightworks.com
#   Date: Dec 20, 2015
#----------------------------------------------------------------------------
from __future__ import print_function, division

from collections import namedtuple
from math import sqrt


StateVec = namedtuple('StateVec', 'phase distTraveled currVelocity fuelConsumed fuelRemaining tEnd')

#----------------------------------------------------------------------------
class DockSim(object):
    """ DockSim contains the flight profile simulation parameters and computes
        simulation output values.
    """
    MAX_V_DOCK = 0.1  # max terminal velocity for successful dock in m/sec
    MIN_V_DOCK = 0.01 # min terminal velocity for successful dock in m/sec
    INITIAL_V  = 0.0  # velocity at start of simulation in m/sec
    
    START_PHASE = 0
    ACCEL_PHASE = 1
    COAST_PHASE = 2
    DECEL_PHASE = 3
    GLIDE_PHASE = 4
    END_PHASE   = 5
    
    PHASE_STR = { START_PHASE: "START",
                  ACCEL_PHASE: "ACCELERATION",
                  COAST_PHASE: "COAST",
                  DECEL_PHASE: "DECELERATION",
                  GLIDE_PHASE: "GLIDE",
                  END_PHASE  : "END",
                }
    MAX_FLIGHT_DURATION_S = 1000 * 60  # 1000 minutes
    
    def __init__(self, tAft, tCoast, tFore, aAft, aFore, rFuel, qFuel, dist):
        """ Store the simulation parameters """
        # User-supplied flight profile parameters
        self.tAft   = tAft   # sec (aft acceleration burn)
        self.tCoast = tCoast # sec (coasting interval)
        self.tFore  = tFore  # sec (forward deceleration burn)
        
        # Capsule flight characteristics parameters
        self.aAft  = aAft  # m/sec^2 (aft acceleration)
        self.aFore = aFore # m/sec^2 (forward deceleration)
        self.rFuel = rFuel # kg/sec (fuel consumption rate)
        self.qFuel = qFuel # kg (initial fuel quantity)
        self.dist  = dist  # m (initial distance to dock)
        self.v0    = self.INITIAL_V # m/sec (initial velocity)
    
    def flightDuration(self):
        """ Return the total duration of the docking maneuver.
            Return None if the terminal velocity is < 0.
        """
        stateVec = self.computeAccelPhase(self.tAft)
        if stateVec.phase == self.END_PHASE:
            # Capsule reached port during acceleration phase
            tEnd = stateVec.tEnd
        else:
            stateVec = self.computeCoastPhase(self.tAft + self.tCoast, stateVec)
            if stateVec.phase == self.END_PHASE:
                # Capsule reached port during coast phase
                tEnd = stateVec.tEnd
            else:
                stateVec = self.computeDecelPhase(self.tAft + self.tCoast + self.tFore, stateVec)
                if stateVec.phase == self.END_PHASE:
                    # Capsule reached port during deceleration phase
                    tEnd = stateVec.tEnd
                else:
                    stateVec = self.computeGlidePhase(t=None, stateVec=stateVec)
                    if stateVec.phase == self.END_PHASE:
                        # Capsule reached port during glide phase
                        tEnd = stateVec.tEnd
        return tEnd
    
    def accelVelocity(self):
        """ Return the velocity at the end of the acceleration phase """
        return self.shipState(self.tAft).currVelocity
    
    def coastVelocity(self):
        """ Return the velocity during the coast phase """
        return self.shipState(self.tAft + self.tCoast).currVelocity
    
    def decelVelocity(self):
        """ Return the velocity at the end of the deceleration phase """
        return self.shipState(self.tAft + self.tCoast + self.tFore).currVelocity
    
    def terminalVelocity(self):
        """ Return the terminal velocity of the maneuver. """
        return self.shipState(self.flightDuration()).currVelocity
    
    def dockIsSuccessful(self):
        """ Return True if the ship docks with a terminal velocity
            between MIN_V_DOCK and MAX_V_DOCK.
        """
        v = self.terminalVelocity()
        return v >= self.MIN_V_DOCK and v <= self.MAX_V_DOCK
    
    def computeAccelPhase(self, t):
        """ Computes a state vector for an acceleration phase of time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, tEnd)
        """
        phase = self.ACCEL_PHASE
        distTraveled = self.v0 * t + 0.5 * self.aAft * t * t
        
        # Have we passed the destination?
        if distTraveled > self.dist:
            phase = self.END_PHASE
            t = (-self.v0 + sqrt(self.v0**2 - 2 * self.aAft * (-self.dist))) / self.aAft
            
        currVelocity = self.v0 + self.aAft * t
        fuelConsumed = min(self.rFuel * t, self.qFuel)
        fuelRemaining = self.qFuel - fuelConsumed
        return StateVec(phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, t)
        
    def computeCoastPhase(self, t, stateVec):
        """ Computes a state vector for the coast phase at time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, tEnd)
        """
        phase = self.COAST_PHASE
        dt = t - stateVec.tEnd
        distTraveled = stateVec.distTraveled + stateVec.currVelocity * dt
        
        # Have we passed the destination?
        if distTraveled > self.dist:
            phase = self.END_PHASE
            dt = (self.dist - stateVec.distTraveled) / stateVec.currVelocity
            t = stateVec.tEnd + dt
            
        currVelocity = stateVec.currVelocity
        fuelConsumed = stateVec.fuelConsumed
        fuelRemaining = stateVec.fuelRemaining
        return StateVec(phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, t)
        
    def computeDecelPhase(self, t, stateVec):
        """ Computes a state vector for the deceleration phase at time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, tEnd)
        """
        phase = self.DECEL_PHASE
        dt = t - stateVec.tEnd
        distTraveled = stateVec.distTraveled + stateVec.currVelocity * dt + 0.5 * (-self.aFore) * dt * dt
        
        # Have we passed the destination?
        if distTraveled > self.dist:
            phase = self.END_PHASE
            dt = (-stateVec.currVelocity + sqrt(stateVec.currVelocity**2 - 2 * (-self.aFore) * (stateVec.distTraveled - self.dist))) / (-self.aFore)
            t = stateVec.tEnd + dt
            
        currVelocity = stateVec.currVelocity + (-self.aFore) * dt
        fuelConsumed = min(stateVec.fuelConsumed + self.rFuel * dt, self.qFuel)
        fuelRemaining = self.qFuel - fuelConsumed
        return StateVec(phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, t)
        
    def computeGlidePhase(self, t, stateVec):
        """ Computes a state vector for the glide phase at time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, tEnd)
        """
        phase = self.GLIDE_PHASE
        distTraveled = stateVec.distTraveled
        if t is not None:
            dt = t - stateVec.tEnd
            distTraveled = stateVec.distTraveled + stateVec.currVelocity * dt
        
        # Have we passed the destination?
        if t is None or distTraveled > self.dist:
            phase = self.END_PHASE
            dt = (self.dist - stateVec.distTraveled) / stateVec.currVelocity
            t = stateVec.tEnd + dt
            
        currVelocity = stateVec.currVelocity
        fuelConsumed = stateVec.fuelConsumed
        fuelRemaining = stateVec.fuelRemaining
        return StateVec(phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, t)
        
    def shipState(self, t):
        """ Return ship state vector for time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, tEnd)
        """
        ## TODO: Handle running out of fuel during any phase
        if t < self.tAft:
            stateVec = self.computeAccelPhase(t)
        else:
            stateVec = self.computeAccelPhase(self.tAft)
            if (t - self.tAft) < self.tCoast:
                stateVec = self.computeCoastPhase(t, stateVec)
            else:
                stateVec = self.computeCoastPhase(self.tAft + self.tCoast, stateVec)
                if (t -  self.tAft - self.tCoast) < self.tFore:
                    stateVec = self.computeDecelPhase(t, stateVec)
                else:
                    stateVec = self.computeDecelPhase(self.tAft + self.tCoast + self.tFore, stateVec)
                    stateVec = self.computeGlidePhase(t, stateVec)
        return stateVec


#----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
#     import unittest
#     
#     class DockSimTestCase(unittest.TestCase):
#         def testInit(self):
#             pass
#         
# #         def testEq(self):
# #             obj = DockSim()
# #             self.assertEqual(obj, 42)
#     
#     unittest.main()  # run the unit tests

    ds = DockSim(tAft=8.2, tCoast=0, tFore=13.1, aAft=0.15, aFore=0.09, rFuel=0.7, qFuel=20, dist=15.0)
#     ds = DockSim(tAft=2, tCoast=2, tFore=13.1, aAft=0.15, aFore=0.09, rFuel=0.7, qFuel=20, dist=15.0)
    t = 0.0
#    s = ds.shipState(11.0)
    while True:
        s = ds.shipState(t)
        print("{}: {}".format(t, s))
        if s.phase == DockSim.END_PHASE:
            break
        t += 1.0

    print("dockIsSuccessful:", ds.dockIsSuccessful())
    print("terminalVelocity:", ds.terminalVelocity())
    print("flightDuration:", ds.flightDuration())
    print("StateVec:", ds.shipState(ds.flightDuration()))
    sys.exit(0)
