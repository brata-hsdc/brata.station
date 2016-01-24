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


# An object to hold the flight profile parameters
#   tAft    is the duration of the acceleration burn, in seconds
#   tCoast  is the duration of the coast phase, in seconds
#   tFore   is the duration of the deceleration burn, in seconds
#   aAft    is the force of acceleration, in m/sec^2
#   aFore   is the force of deceleration, in m/sec^2
#   rFuel   is the rate of fuel consumption in kg/sec
#   qFuel   is the initial amount of fuel, in kg
#   dist    is the initial distance to the dock, in m
#   vMin    is the minimum sucessful docking velocity, in m/s
#   vMax    is the maximum sucessful docking velocity, in m/s
#   vInit   is the ship's initial velocity, in m/s
#   tSim    is the maximum duration of the simulation in seconds (an int)
FlightParams = namedtuple('FlightParams', 'tAft tCoast tFore aAft aFore rFuel qFuel dist vMin vMax vInit tSim')

StateVec = namedtuple('StateVec', 'phase distTraveled currVelocity fuelRemaining tEnd')

#----------------------------------------------------------------------------
class DockSim(object):
    """ DockSim contains the flight profile simulation parameters and computes
        simulation output values.
    """
    # Flight parameters
    # (TODO: should come from MS Settings table)
    MAX_V_DOCK = 0.1  # max terminal velocity for successful dock in m/sec
    MIN_V_DOCK = 0.01 # min terminal velocity for successful dock in m/sec
    INITIAL_V  = 0.0  # velocity at start of simulation in m/sec
    
    # Longest flight time allowed
    # (must be greater than maximum burn length self.qFuel/self.rFuel)
    # (TODO: should come from MS Settings table)
    MAX_FLIGHT_DURATION_S = 1000 * 60  # 1000 minutes
    
    # Flight phases
    START_PHASE = 0
    ACCEL_PHASE = 1
    COAST_PHASE = 2
    DECEL_PHASE = 3
    GLIDE_PHASE = 4
    END_PHASE   = 5
    
    PHASE_STR = { START_PHASE: "START",
                  ACCEL_PHASE: "ACCELERATE",
                  COAST_PHASE: "COAST",
                  DECEL_PHASE: "DECELERATE",
                  GLIDE_PHASE: "GLIDE",
                  END_PHASE  : "END",
                }

    # Status value returned at end of travel interval computation    
    INTERVAL_DNF  = 0  # Did not finish
    INTERVAL_DEST = 1  # Dest reached
    INTERVAL_END  = 2  # End of time interval reached
    
    # Final simulation result conditions
    OUTCOME_DNF      = "OUTCOME_DNF"
    OUTCOME_NO_FUEL  = "OUTCOME_NO_FUEL"
    OUTCOME_TOO_SLOW = "OUTCOME_TOO_SLOW"
    OUTCOME_TOO_FAST = "OUTCOME_TOO_FAST"
    OUTCOME_SUCCESS  = "OUTCOME_SUCCESS"
    
    def __init__(self, fp):
        """ Store the simulation parameters.
            fp is a FlightParams namedtuple.
            Raises ValueError if any of the flight characteristics are out of
            range, but allows the user-supplied time values to be anything.
        """
        # User-supplied flight profile parameters
        self.tAft   = fp.tAft   # sec (aft acceleration burn)
        self.tCoast = fp.tCoast # sec (coasting interval)
        self.tFore  = fp.tFore  # sec (forward deceleration burn)
        
        # Capsule flight characteristics parameters
        self.aAft  = fp.aAft  # m/sec^2 (aft acceleration)
        self.aFore = fp.aFore # m/sec^2 (forward deceleration)
        self.rFuel = fp.rFuel # kg/sec (fuel consumption rate)
        self.qFuel = fp.qFuel # kg (initial fuel quantity)
        self.dist  = fp.dist  # m (initial distance to dock)
        self.vMin  = fp.vMin  # m/s (min docking velocity)
        self.vMax  = fp.vMax  # m/s (max docking velocity)
        self.v0    = fp.vInit # m/sec (initial velocity)
        
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
    
    def outcome(self, state):
        """ Determine the nature of the failure from the final state """
        status = self.OUTCOME_SUCCESS

        if state.currVelocity <= 0.0:
            status = self.OUTCOME_DNF
        elif state.fuelRemaining <= 0.0:
            status = self.OUTCOME_NO_FUEL
        elif state.currVelocity < self.vMin:
            status = self.OUTCOME_TOO_SLOW
        elif state.currVelocity > self.vMax:
            status = self.OUTCOME_TOO_FAST

        return status
        
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
        return v >= self.vMin and v <= self.vMax
        
    def dockIsSuccessful(self):
        """ Return True if the ship docks with a terminal velocity
            between self.vMin and self.vMax.
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
        """ Compute resulting velocity from initial velocity, accel, and time interval """
        return v0 + a * dt
    
    def fuelConsumed(self, dt):
        """ Compute amount of fuel consumed by a burn of dt """
        return dt * self.rFuel  # time * rate of consumption
    
    def timeToTravel(self, d, v0, a):
        """ Return the time it takes to traverse a distance, d.
        
            d  is the distance to be traversed, in meters (d >= 0)
            v0 is the initial velocity, in m/s
            a  is the constant acceleration, in m/s**2
            
            Returns the positive time in seconds to go the distance d,
            or the negative time it takes for the velocity to go to 0
            if a negative acceleration causes the velocity to go negative,
            or None if v0 <= 0
            
            Note:  This may handle more cases than it needs to, but that's
                   okay.
        """
        if a == 0.0:
            if v0 == 0.0:
                return None
            else:
                return d/v0
        else:
            disc = v0**2 - 2.0 * a * (-d)
            if disc < 0.0:
                # Negative acceleration will cause the velocity to go negative,
                # also resulting in no real solution for the time
                # so instead we will return the time it takes the velocity to go to zero
                return v0/a # either v0 or a is negative
            else:
                return (-v0 + sqrt(v0**2 - 2.0 * a * (-d))) / a
    
    def timeToStop(self, v0, a):
        """ Return the time it takes for velocity to go to zero.
        
            v0 must be >= 0.0 or ValueError is raised.
            a must be < 0.0 or ValueError is raised.
            
            Returns the time in seconds for the initial velocity to be
            reduced to zero.
        """
        if a >= 0.0:
            raise ValueError("a must be < 0.0")
        if v0 < 0.0:
            raise ValueError("v0 must be >= 0.0")
        
        # Use:  v = v0 + a * t
        # Solve for v = 0:
        #   v0 + a * t = 0
        #   t = -v0/a
        return -v0/a
    
    def timeUntilFuelRunsOut(self, qFuel):
        """ Return the burn time until fuel is completely consumed.
            qFuel is the amount of fuel, in kg.
            Assumes constant burn rate, self.rFuel.
            
            Returns the time in seconds of the maximum burn.
        """
        return qFuel/self.rFuel
    
    
    def computeNoThrustTravelInterval(self, dt, v0, distToDest, qFuel):
        """ Compute distance traveled, ending velocity, time remaining, and end condition.
            Assumes acceleration is 0 (no thrust), so fuel is not an issue.
            The initial velocity, v0, and the quantity of fuel, qFuel, are
            passed in, but are just passed through unchanged.
            
            Return a tuple (distanceTraveled, v0, qFuel, timeRemaining, endCondition)
        """
        # Are we there already?
        if distToDest <= 0.0:
            return(0.0,  # did not take any time to reach dest
                   v0,   # velocity unchanged
                   qFuel,  # fuel quantity unchanged
                   dt,  # no time used
                   self.INTERVAL_DEST  # destination was reached
                  )
            
        # Compute time to reach destination
        tDest = self.timeToTravel(distToDest, v0, 0.0)
        
        # If tDest is None, the destination will never be reached because the
        # velocity is 0 or negative
        if tDest is None:
            return (0.0,  # say that no distance toward the target was traversed
                    v0,  # velocity unchanged
                    qFuel,  # fuel quantity unchanged
                    dt,  # say that no time was used progressing to the dest
                    self.INTERVAL_DNF
                   )
        else:
            if tDest < dt:
                # Destination was reached within this time interval
                return (distToDest,  # distance to dest was traversed
                        v0,  # velocity unchanged
                        qFuel,  # fuel quantity unchanged
                        dt - tDest,  # time remaining in interval
                        self.INTERVAL_DEST  # destination was reached
                       )
            else:
                # Reached end of time interval before reaching dest
                return (self.distanceTraveled(dt, v0),  # the distance that was traveled
                        v0,  # velocity unchanged
                        qFuel,  # fuel quantity unchanged
                        0.0,  # end of interval reached
                        self.INTERVAL_END
                       )
                
    def computeTravelInterval(self, dt, v0, a, distToDest, qFuel):
        """ Compute distance traveled, velocity, and fuel consumed.
 
            Correctly handles running out of fuel part way through
            the interval.  Also checks whether the ship would travel
            past the destination.
             
            If the destination is reached during dt, the values are
            returned with dist = distToDest, and v = the final velocity
            at docking (not 0).
             
            Return a tuple (distanceTraveled, endVelocity, fuelRemaining, timeRemaining, endCondition)
        """
        # Validate the inputs
        if distToDest <= 0.0:  # we are done
            return (0.0, # already at (or past) dest
                    v0,  # velocity unchanged
                    qFuel,  # fuel quantity unchanged
                    dt,  # no time used
                    self.INTERVAL_DEST  # destination reached
                   )
        if dt <= 0.0:
            return (0.0, # position unchanged
                    v0,  # velocity unchanged
                    qFuel,  # fuel quantity unchanged
                    dt,  # no time used
                    self.INTERVAL_END  # end of time interval
                   )
        if v0 < 0.0:
            raise ValueError("v0 must be >= 0.0")
        
        # If there is no acceleration or deceleration, do a simpler
        # constant velocity computation
        if a == 0.0:
            return self.computeNoThrustTravelInterval(dt, v0, distToDest, qFuel)
        
        # Compute how long the engines can fire before fuel runs out
        tFuel = self.timeUntilFuelRunsOut(qFuel)
        
        # If the craft is decelerating, it could stop or reverse before reaching the
        # destination. If so, determine the time until v crosses 0 (how long the engines
        # can fire before the ship stops making progress toward the destination).
        # Otherwise, set tStop to a really big number.
        if a < 0.0:
            tStop = self.timeToStop(v0, a)
        else:
            tStop = self.MAX_FLIGHT_DURATION_S

        # The time under acceleration is the shorter of the time until the ship
        # stops due to deceleration, or the time until the fuel runs out
        tAccel = min(tFuel, tStop)
        
        # Compute the distance traveled during the time under acceleration
        distTraveled = self.distanceTraveled(tAccel, v0, a)
        
        # Is dest reached while under acceleration (with engines firing), which
        # is True if the distTraveled under acceleration would be greater than the
        # distance to the destination.  If so, shorten the time under acceleration
        # to the time until the destination is reached, and set the distance traveled
        # to be the distance to the dest.
        if distTraveled >= distToDest:
            tAccel = self.timeToTravel(distToDest, v0, a)
            distTraveled = distToDest

        # Does the end of the time interval occur before dest reached or fuel runs out
        # i.e., while the ship is still accelerating?  If so, it is straightforward to
        # calculate the state values using dt.
        if dt < tAccel:
            return (self.distanceTraveled(dt, v0, a),  # dist traveled during interval
                    self.velocity(dt, v0, a),  # velocity at end of interval
                    qFuel - self.fuelConsumed(dt),  # fuel remaining 
                    0.0,  # entire interval used
                    self.INTERVAL_END  # dest not reached yet
                   )
        
        # If this code is reached, the ship either ran out of fuel, or the velocity
        # went to zero or negative.  If the time under acceleration is the same as
        # the time until v = 0, then the velocity went to zero before fuel ran out.
        # The destination will never be reached, so compute values for the time
        # interval up to where v goes to zero.
        if tAccel == tStop:
            # Flight will never reach destination
            return (self.distanceTraveled(tStop, v0, a),  # forward progress made
                    0.0,  # ship stopped
                    qFuel - self.fuelConsumed(tStop),  # fuel remaining
                    dt - tStop,  # time remaining after ship stopped
                    self.INTERVAL_DNF  # dest will not be reached
                   )
            
        # Either dest reached (tAccel < tFuel) or fuel runs out, continue at constant velocity
        cDist,cVel,cFuel,cTime,cState = self.computeNoThrustTravelInterval(dt - tAccel,  # time remaining after acceleration
                                                                   self.velocity(tAccel, v0, a),  # velocity after acceleration
                                                                   distToDest - self.distanceTraveled(tAccel, v0, a),  # dist remaining after acceleration
                                                                   0.0 if tFuel < tAccel else qFuel - self.fuelConsumed(tAccel) # fuel remaining
                                                                  )
        return (self.distanceTraveled(tAccel, v0, a) + cDist,  # total dist after both phases
                cVel,   # final velocity is passed through
                cFuel,  # final fuel quantity is passed through (0.0)
                cTime,  # whatever is left after constV phase
                cState  # final state is state at end of constV phase
               )
        
    def currPhase(self, t):
        """ Return the flight phase for time t. """
        if   t <= 0.0: return self.START_PHASE
        elif t <= self.tAft: return self.ACCEL_PHASE
        elif t <= self.tAft + self.tCoast: return self.COAST_PHASE
        elif t <= self.tAft + self.tCoast + self.tFore: return self.DECEL_PHASE
        else: return self.GLIDE_PHASE

    def nextPhase(self, phase):
        """ Return the next flight phase after phase """
        return {self.START_PHASE: self.ACCEL_PHASE,
                self.ACCEL_PHASE: self.COAST_PHASE,
                self.COAST_PHASE: self.DECEL_PHASE,
                self.DECEL_PHASE: self.GLIDE_PHASE,
                self.GLIDE_PHASE: self.END_PHASE,
                self.END_PHASE  : self.END_PHASE,
                }[phase]
    
    def acceleration(self, phase):
        """ Return the acceleration amount for the specified phase """
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
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelRemaining, tEnd)
        """
        phase = self.nextPhase(stateVec.phase)
        accel = self.acceleration(phase)
        dt = t - stateVec.tEnd  # time delta between end of last phase and t
        distRemaining = self.dist - stateVec.distTraveled
        
        d,v,fuelRemaining,tRemaining,intervalStatus = self.computeTravelInterval(dt, stateVec.currVelocity, accel, distRemaining, stateVec.fuelRemaining)
        
        endTime = stateVec.tEnd + dt - tRemaining
        
        if intervalStatus in (self.INTERVAL_DNF, self.INTERVAL_DEST):
            phase = self.END_PHASE

        return StateVec(phase, d + stateVec.distTraveled, v, fuelRemaining, endTime)
    
    def flightDuration(self):
        """ Return the total duration of the docking maneuver.
            Return None if the terminal velocity is < 0.
        """
        stateVec = self.shipState(self.tAft + self.tCoast + self.tFore)
        if stateVec.phase == self.END_PHASE:
            tEnd = stateVec.tEnd
        else:
            if stateVec.currVelocity <= 0.0:
                tEnd = None
            else:
                # Compute coast time
                tEnd = stateVec.tEnd + self.timeToTravel(self.dist - stateVec.distTraveled, stateVec.currVelocity, 0.0)
        return tEnd
    
    def shipState(self, t):
        """ Return ship state vector for time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelRemaining, tEnd)
        """
        # Create initial stateVec
        stateVec = StateVec(phase=self.START_PHASE,
                            distTraveled=0.0,
                            currVelocity=self.v0,
                            fuelRemaining=self.qFuel,
                            tEnd=0.0)

        # Create an array containing the ending time of each flight phase (accel, coast, decel)
        phaseTimes = [self.tAft, self.tAft + self.tCoast, self.tAft + self.tCoast + self.tFore]
        
        # Sequentially calculate the flight phases until the simulation state reaches END_PHASE
        while stateVec.phase != self.END_PHASE:
            if phaseTimes and t > phaseTimes[0]:
                stateVec = self.computePhase(phaseTimes[0], stateVec)
                phaseTimes = phaseTimes[1:]
            else:
                # Compute the final time segment
                stateVec = self.computePhase(t, stateVec)
                break
            
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

    fp = FlightParams(tAft=9.2,#8.4#8.3
                      tCoast=1, #0
                      tFore=13.1,
                      aAft=0.15,
                      aFore=0.09,
                      rFuel=0.7,
                      qFuel=20,
                      dist=15.0,
                      vMin=0.01,
                      vMax=0.1,
                      vInit=0.0,
                      tSim=45,
                     )
    ds = DockSim(fp)
#     ds = DockSim(tAft=2, tCoast=2, tFore=13.1, aAft=0.15, aFore=0.09, rFuel=0.7, qFuel=20, dist=15.0)
    t = 0.0
#    s = ds.shipState(11.0)
    while True:
        if t == 17.0:
            pass
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
