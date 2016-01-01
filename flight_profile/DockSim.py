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
        """ Store the simulation parameters.
            Raises ValueError if any of the flight characteristics are out of
            range, but allows the user-supplied time values to be anything.
        """
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
        
        # Validate some parameters
        if self.rFuel <= 0.0:
            raise ValueError("Fuel consumption rate must be greater than 0 if you hope to get anywhere")
        if self.qFuel <= 0.0:
            raise ValueError("Fuel quantity must be greater than 0 if you hope to get anywhere")
        if self.dist <= 0.0:
            raise ValueError("Distance to travel must be greater than 0")
        if self.aFore <= 0.0:
            raise ValueError("Fore thruster (nose maneuvering jets) acceleration must be greater than 0")
        if self.aAft <= 0.0:
            raise ValueError("Aft thruster (rear engine) acceleration must be greater than 0")
    
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
    
    def distanceTraveled(self, dt, v0, a=0.0):
        """ Compute the distance traveled.
        
            dt  is the amount of time traveled, in seconds
            v0  is the velocity at the start of the time interval, in m/s
            a   is the amount of constant acceleration being applied during
                the interval, in m/s^2
            
            Returns the distance traveled during the timeInterval, in meters
            computed by the formula  d = v0 * dt + 0.5 * a * dt**2
        """
        return (v0 + 0.5 * a * dt) * dt
    
    def velocity(self, dt, v0, a):
        return v0 + a * dt
    
    def timeToTravel(self, d, v0, a):
        """ Return the time it takes to traverse a distance, d.
        
            d  is the distance to be traversed, in meters (d >= 0)
            v0 is the initial velocity, in m/s
            a  is the constant acceleration, in m/s**2
            
            Returns the time in seconds, or None if v0 <= 0
        """
        if v0 <= 0:
            return None
        if a == 0.0:
            return d/v0
        else:
            return (-v0 + sqrt(v0**2 - 2 * a * (-d))) / a
    
    def computePhase(self, dt, v0, a, qFuel):
        """ Compute distance traveled, velocity, and fuel consumed.
            Return a tuple (dist, v, fuelConsumed)
        """
        dist = 0.0
        v = v0
        fuelConsumed = 0.0
        
        if dt > 0.0:
            if a != 0.0:
                # Will be consuming fuel
                fuelConsumed = self.rFuel * dt
                if fuelConsumed > qFuel:  # fuel runs out
                    tBurn = self.qFuel/self.rFuel
                    dist,v0,fuelConsumed = self.computePhase(tBurn, v0, a)
                    a = 0.0  # can't accelerate any more (no fuel left)
                    dt = dt - tBurn  # remaining time will be coasting
            
            # If we ran out of fuel, a == 0
            dist += self.distanceTraveled(dt, v0, a)
            v = self.velocity(dt, v0, a)
        
        return (dist, v, fuelConsumed)
        
    def computeAccelPhase(self, t):
        """ Computes a state vector for an acceleration phase of time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, tEnd)
        """
        phase = self.ACCEL_PHASE
        distTraveled = 0.0
        accel = self.aAft
        
        d,v,fuelConsumed = self.computePhase(t, self.v0, accel, self.qFuel)
        if d + distTraveled > self.dist: # went past the destination
            # Compute time to reach dest
            t = self.timeToTravel(self.dist, self.v0, accel)
            d,v,fuelConsumed = self.computePhase(t, self.v0, accel, self.qFuel)
            phase = self.END_PHASE
            
        fuelRemaining = self.qFuel - fuelConsumed
        return StateVec(phase, d + distTraveled, v, fuelConsumed, fuelRemaining, t)
    
    def computeCoastPhase(self, t, stateVec):
        """ Computes a state vector for the coast phase at time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, tEnd)
        """
        phase = self.COAST_PHASE
        dt = t - stateVec.tEnd
        distTraveled = stateVec.distTraveled
        accel = 0.0

        d,v,fuelConsumed = self.computePhase(dt, stateVec.currVelocity, accel, stateVec.fuelRemaining)
        if d + distTraveled > self.dist: # went past the destination
            # Compute time to reach dest
            dt = self.timeToTravel(d, stateVec.currVelocity, accel)
            d,v,fuelConsumed = self.computePhase(dt, stateVec.currVelocity, accel, stateVec.fuelRemaining)
            phase = self.END_PHASE
            
        fuelRemaining = stateVec.fuelRemaining - fuelConsumed
        return StateVec(phase, d + distTraveled, v, fuelConsumed, fuelRemaining, stateVec.tEnd + dt)
        
    def computeDecelPhase(self, t, stateVec):
        """ Computes a state vector for the deceleration phase at time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, tEnd)
        """
        phase = self.DECEL_PHASE
        dt = t - stateVec.tEnd
        distTraveled = stateVec.distTraveled
        accel = -self.aFore
        
        d,v,fuelConsumed = self.computePhase(dt, stateVec.currVelocity, accel, stateVec.fuelRemaining)
        if d + distTraveled > self.dist: # went past the destination
            # Compute time to reach dest
            dt = self.timeToTravel(d, stateVec.currVelocity, accel)
            d,v,fuelConsumed = self.computePhase(dt, stateVec.currVelocity, accel, stateVec.fuelRemaining)
            phase = self.END_PHASE
            
        fuelRemaining = stateVec.fuelRemaining - fuelConsumed
        return StateVec(phase, d + distTraveled, v, fuelConsumed, fuelRemaining, stateVec.tEnd + dt)

    def computeGlidePhase(self, t, stateVec):
        """ Computes a state vector for the glide phase at time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, tEnd)
        """
        phase = self.GLIDE_PHASE
        dt = t - stateVec.tEnd
        distTraveled = stateVec.distTraveled
        accel = 0.0
        
        d,v,fuelConsumed = self.computePhase(dt, stateVec.currVelocity, accel, stateVec.fuelRemaining)
        if d + distTraveled > self.dist: # went past the destination
            # Compute time to reach dest
            dt = self.timeToTravel(d, stateVec.currVelocity, accel)
            d,v,fuelConsumed = self.computePhase(dt, stateVec.currVelocity, accel, stateVec.fuelRemaining)
            phase = self.END_PHASE
            
        fuelRemaining = stateVec.fuelRemaining - fuelConsumed
        return StateVec(phase, d + distTraveled, v, fuelConsumed, fuelRemaining, stateVec.tEnd + dt)
        
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
                    t = self.timeToTravel(self.dist - stateVec.distTraveled, stateVec.currVelocity, 0.0)
                    if t is not None:
                        # Capsule reached port during glide phase
                        tEnd = stateVec.tEnd + t
                    else:
                        tEnd = None
        return tEnd
    
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
            if stateVec.phase != self.END_PHASE:
                if (t - self.tAft) < self.tCoast:
                    stateVec = self.computeCoastPhase(t, stateVec)
                else:
                    stateVec = self.computeCoastPhase(self.tAft + self.tCoast, stateVec)
                    if stateVec.phase != self.END_PHASE:
                        if (t -  self.tAft - self.tCoast) < self.tFore:
                            stateVec = self.computeDecelPhase(t, stateVec)
                        else:
                            stateVec = self.computeDecelPhase(self.tAft + self.tCoast + self.tFore, stateVec)
                            if stateVec.phase != self.END_PHASE:
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
