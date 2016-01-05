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
    
    def safeDockingVelocity(self, v):
        """ Return True if v is in the safe docking range """
        return v >= self.MIN_V_DOCK and v <= self.MAX_V_DOCK
        
    def dockIsSuccessful(self):
        """ Return True if the ship docks with a terminal velocity
            between MIN_V_DOCK and MAX_V_DOCK.
        """
        return self.safeDockingVelocity(self.terminalVelocity())
    
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
        if a == 0.0:
            if v0 == 0.0:
                return None
            else:
                return d/v0
        else:
            return (-v0 + sqrt(v0**2 - 2.0 * a * (-d))) / a
    
    def computeTravelInterval(self, dt, v0, a, distToDest, qFuel):
        """ Compute distance traveled, velocity, and fuel consumed.

            Correctly handles running out of fuel part way through
            the interval.  Also checks whether the ship would travel
            past the destination.
            
            If the destination is reached during dt, the values are
            returned with dist = distToDest, and v = the final velocity
            at docking (not 0).
            
            Return a tuple (distanceTraveled, endVelocity, fuelRemaining, timeRemaining)
        """
        dist = 0.0             # total distance traveled during dt
        v = v0                 # current velocity
        fuelRemaining = qFuel  # amount of fuel in the tank
        timeRemaining = 0.0    # time left if dest reached before end of dt
        
        fuelConsumptionRate = 0.0 if a == 0.0 else self.rFuel
        
        if dt > 0.0:
#             if a != 0.0:
            # There is acceleration (which could be negative), so we are
            # consuming fuel.
            # We need to figure out the situation:
            #  1. a != 0: accelerate until dt
            #  2. Accelerate until dest is reached
            #  3. a == 0, or accelerate until we run out of fuel:
            #     a. ...then glide until dt
            #     b. ...then glide until dest
            
            # Check if we will run out of fuel before dt
#             if fuelRemaining < fuelConsumptionRate * dt: # it will run out

            #   How far will we go before the fuel runs out?
            #   Solve for t:  fuelRemaining = self.rFuel * t
            tAccel = min(dt, 0.0 if fuelConsumptionRate <= 0.0 else (fuelRemaining/fuelConsumptionRate))  # burn duration
            dAccel = self.distanceTraveled(tAccel, v, a)  # burn distance
            
            # Condition #2 or #3, or #1 with a == 0:
            # Check if we will run out of fuel before reaching dest
            if dAccel >= distToDest: # burn the entire way
                # Condition #2, or #1 with a != 0:
                #   Compute time until dest is reached
                tAccel = self.timeToTravel(dAccel, v, a)
                dist = distToDest
                v = self.velocity(tAccel, v, a)
                timeRemaining = dt - tAccel
            else:
                # Condition #3 (a == 0, or fuel runs out), or Condition #1:
                #   Compute the velocity at end of burn
                vConst = self.velocity(tAccel, v, a)  # v at end of acceleration
                dConstVel = self.distanceTraveled(dt - tAccel, vConst, 0.0)  # dist traveled at const v in remaining time
                
                # Check if we will reach dest before dt
                if dAccel + dConstVel < distToDest: # dest not reached during dt
                    # Condition #3a:
                    #   Compute how far it gets by the end of the time interval
                    dist = dAccel + dConstVel
                    v = vConst
                else:
                    # Condition #3b:
                    #   Destination reached
                    dist = distToDest
                    v = vConst
                    timeRemaining = dt - self.timeToTravel(dist, v, 0.0)
                    
            fuelRemaining = max(0.0, qFuel - fuelConsumptionRate * tAccel)
#             else:
#                 # Condition #1 with a != 0:
#                 dist = self.distanceTraveled(dt, v, a)
#                 v = self.velocity(dt, v, a)
#                 fuelRemaining = qFuel - fuelConsumptionRate * dt
#                 timeRemaining = 0.0

#             else:
#                 # Constant velocity, no acceleration        
#                 dist = self.distanceTraveled(dt, v, 0.0)
#                 v = self.velocity(dt, v, 0.0)
#                 fuelRemaining = qFuel
#                 timeRemaining = 0
                    
#                 fuelRemaining -= self.rFuel * dt
#                 if fuelRemaining <= 0.0:  # fuel runs out
#                     tAccel = qFuel/self.rFuel  # how long we can fire the rockets
#                     dist,distAccel,v,fuelRemaining = self.computeTravelInterval(tAccel, v, a, qFuel)
#                     a = 0.0  # can't accelerate any more (no fuel left)
#                     dt = dt - tAccel  # remaining time will be coasting
#             
#             # If we ran out of fuel, a == 0
#             distConstantVel = self.distanceTraveled(dt, v, a)
#             dist = distAccel + distConstantVel
#             v = self.velocity(dt, v, a)
        
        return (dist, v, fuelRemaining, timeRemaining)
    
    def nextPhase(self, phase):
        return {self.START_PHASE: self.ACCEL_PHASE,
                self.ACCEL_PHASE: self.COAST_PHASE,
                self.COAST_PHASE: self.DECEL_PHASE,
                self.DECEL_PHASE: self.GLIDE_PHASE,
                self.GLIDE_PHASE: self.END_PHASE,
                self.END_PHASE  : self.END_PHASE,
                }[phase]
    
    def acceleration(self, phase):
        return {self.START_PHASE: 0.0,
                self.ACCEL_PHASE: self.aAft,
                self.COAST_PHASE: 0.0,
                self.DECEL_PHASE: -self.aFore,
                self.GLIDE_PHASE: 0.0,
                self.END_PHASE  : 0.0,
                }[phase]
                
    def computePhase(self, t, stateVec):
        """ Computes a state vector for an acceleration phase of time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, tEnd)
        """
        phase = self.nextPhase(stateVec.phase)
        accel = self.acceleration(phase)
        dt = t - stateVec.tEnd  # time delta between end of last phase and t
        distRemaining = self.dist - stateVec.distTraveled
        
        d,v,fuelRemaining,tRemaining = self.computeTravelInterval(dt, stateVec.currVelocity, accel, distRemaining, stateVec.fuelRemaining)
        
#         if d + stateVec.distTraveled > self.dist: # went past the destination
#             # Did we run out of fuel?
#             if fuelRemaining <= 0.0: # then we ran out
#                 # Did we run out before we reached the destination?
#                 # Then compute the solution in two parts: the accelerated part and the constant velocity part
#                 pass
#             else:
#                 # Compute time to reach dest
#                 dt = self.timeToTravel(self.dist - stateVec.distTraveled, stateVec.currVelocity, accel)
#                 d,v,fuelRemaining,tRemaining = self.computeTravelInterval(dt, stateVec.currVelocity, accel, distRemaining, stateVec.fuelRemaining)
#                 phase = self.END_PHASE
                
        if d >= distRemaining: # dest was reached
            phase = self.END_PHASE
            dt -= tRemaining
            
#         fuelRemaining = self.qFuel - (stateVec.fuelConsumed + fuelConsumed)
#         return StateVec(phase, d + stateVec.distTraveled, v, stateVec.fuelConsumed + fuelConsumed, fuelRemaining, stateVec.tEnd + dt)
        return StateVec(phase, d + stateVec.distTraveled, v, self.qFuel - fuelRemaining, fuelRemaining, stateVec.tEnd + dt)
    
    def computeAccelPhase(self, t, stateVec):
        """ Computes a state vector for an acceleration phase of time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, tEnd)
        """
        return self.computePhase(t, stateVec)
    
    def computeCoastPhase(self, t, stateVec):
        """ Computes a state vector for the coast phase at time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, tEnd)
        """
        return self.computePhase(t, stateVec)
        
    def computeDecelPhase(self, t, stateVec):
        """ Computes a state vector for the deceleration phase at time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, tEnd)
        """
        return self.computePhase(t, stateVec)

    def computeGlidePhase(self, t, stateVec):
        """ Computes a state vector for the glide phase at time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelConsumed, fuelRemaining, tEnd)
        """
        return self.computePhase(t, stateVec)
        
    def flightDuration(self):
        """ Return the total duration of the docking maneuver.
            Return None if the terminal velocity is < 0.
        """
        # Create initial stateVec
        stateVec = StateVec(phase=self.START_PHASE,
                            distTraveled=0.0,
                            currVelocity=self.v0,
                            fuelConsumed=0.0,
                            fuelRemaining=self.qFuel,
                            tEnd=0.0)

        # Walk through the individual simulation phases
        stateVec = self.computeAccelPhase(self.tAft, stateVec)
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
        
        # Create initial stateVec
        stateVec = StateVec(phase=self.START_PHASE,
                            distTraveled=0.0,
                            currVelocity=self.v0,
                            fuelConsumed=0.0,
                            fuelRemaining=self.qFuel,
                            tEnd=0.0)

        # Walk through the individual simulation phases
        if t < self.tAft:
            stateVec = self.computeAccelPhase(t, stateVec)
        else:
            stateVec = self.computeAccelPhase(self.tAft, stateVec)
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
