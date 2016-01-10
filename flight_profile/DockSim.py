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
    
    def __init__(self, fp):
        """ Store the simulation parameters.
            fp is a FlightProfile.FlightParams namedtuple.
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
        return v0 + a * dt
    
    def fuelConsumed(self, dt):
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
    
#     def computeTravelInterval(self, dt, v0, a, distToDest, qFuel):
#         """ Compute distance traveled, velocity, and fuel consumed.
# 
#             Correctly handles running out of fuel part way through
#             the interval.  Also checks whether the ship would travel
#             past the destination.
#             
#             If the destination is reached during dt, the values are
#             returned with dist = distToDest, and v = the final velocity
#             at docking (not 0).
#             
#             Return a tuple (distanceTraveled, endVelocity, fuelRemaining, timeRemaining)
#         """
#         dist = 0.0             # total distance traveled during dt
#         v = v0                 # current velocity
#         fuelRemaining = qFuel  # amount of fuel in the tank
#         timeRemaining = 0.0    # time left if dest reached before end of dt
#         
#         fuelConsumptionRate = 0.0 if a == 0.0 else self.rFuel
#         
#         if dt > 0.0:
# #             if a != 0.0:
#             # There is acceleration (which could be negative), so we are
#             # consuming fuel.
#             # We need to figure out the situation:
#             #  1. a != 0: accelerate until dt
#             #  2. Accelerate until dest is reached
#             #  3. a == 0, or accelerate until we run out of fuel:
#             #     a. ...then glide until dt
#             #     b. ...then glide until dest
#             
#             # Check if we will run out of fuel before dt
# #             if fuelRemaining < fuelConsumptionRate * dt: # it will run out
# 
#             #   How far will we go before the fuel runs out?
#             #   Solve for t:  fuelRemaining = self.rFuel * t
#             tAccel = min(dt, 0.0 if fuelConsumptionRate <= 0.0 else (fuelRemaining/fuelConsumptionRate))  # burn duration
#             dAccel = self.distanceTraveled(tAccel, v, a)  # burn distance
#             
#             # Condition #2 or #3, or #1 with a == 0:
#             # Check if we will run out of fuel before reaching dest
#             if dAccel >= distToDest: # burn the entire way
#                 # Condition #2, or #1 with a != 0:
#                 #   Compute time until dest is reached
#                 tAccel = self.timeToTravel(dAccel, v, a)
#                 dist = distToDest
#                 v = self.velocity(tAccel, v, a)
#                 timeRemaining = dt - tAccel
#             else:
#                 # Condition #3 (a == 0, or fuel runs out), or Condition #1:
#                 #   Compute the velocity at end of burn
#                 vConst = self.velocity(tAccel, v, a)  # v at end of acceleration
#                 dConstVel = self.distanceTraveled(dt - tAccel, vConst, 0.0)  # dist traveled at const v in remaining time
#                 
#                 # Check if we will reach dest before dt
#                 if dAccel + dConstVel < distToDest: # dest not reached during dt
#                     # Condition #3a:
#                     #   Compute how far it gets by the end of the time interval
#                     dist = dAccel + dConstVel
#                     v = vConst
#                 else:
#                     # Condition #3b:
#                     #   Destination reached
#                     dist = distToDest
#                     v = vConst
#                     timeRemaining = dt - self.timeToTravel(dist, v, 0.0)
#                     
#             fuelRemaining = max(0.0, qFuel - fuelConsumptionRate * tAccel)
# #             else:
# #                 # Condition #1 with a != 0:
# #                 dist = self.distanceTraveled(dt, v, a)
# #                 v = self.velocity(dt, v, a)
# #                 fuelRemaining = qFuel - fuelConsumptionRate * dt
# #                 timeRemaining = 0.0
# 
# #             else:
# #                 # Constant velocity, no acceleration        
# #                 dist = self.distanceTraveled(dt, v, 0.0)
# #                 v = self.velocity(dt, v, 0.0)
# #                 fuelRemaining = qFuel
# #                 timeRemaining = 0
#                     
# #                 fuelRemaining -= self.rFuel * dt
# #                 if fuelRemaining <= 0.0:  # fuel runs out
# #                     tAccel = qFuel/self.rFuel  # how long we can fire the rockets
# #                     dist,distAccel,v,fuelRemaining = self.computeTravelInterval(tAccel, v, a, qFuel)
# #                     a = 0.0  # can't accelerate any more (no fuel left)
# #                     dt = dt - tAccel  # remaining time will be coasting
# #             
# #             # If we ran out of fuel, a == 0
# #             distConstantVel = self.distanceTraveled(dt, v, a)
# #             dist = distAccel + distConstantVel
# #             v = self.velocity(dt, v, a)
#         
#         return (dist, v, fuelRemaining, timeRemaining)
    
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
#         dist = 0.0             # total distance traveled during dt
#         v = v0                 # current velocity
#         fuelRemaining = qFuel  # amount of fuel in the tank
#         timeRemaining = 0.0    # time left if dest reached before end of dt
#          
#         fuelConsumptionRate = 0.0 if a == 0.0 else self.rFuel
        
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
        
        # If there is no acceleration, do a simpler computation
        if a == 0.0:
            return self.computeNoThrustTravelInterval(dt, v0, distToDest, qFuel)
        
        # Compute how long the engines can fire before fuel runs out
        tFuel = self.timeUntilFuelRunsOut(qFuel)
        
        if a < 0.0:
            # The craft is slowing, and could stop or reverse before reaching the
            # destination, so determine when v crosses 0 (how long the engines
            # can fire before the ship stops making progress toward the destination).
            tStop = self.timeToStop(v0, a)
        else:
            tStop = self.MAX_FLIGHT_DURATION_S

        tAccel = min(tFuel, tStop)  # time under acceleration
        
        # Compute the distance traveled under acceleration
        distTraveled = self.distanceTraveled(tAccel, v0, a)
        
        # Is dest reached with engines firing?
        if distTraveled >= distToDest:
            # Yes:  compute how long that takes
            tAccel = self.timeToTravel(distToDest, v0, a)

        # Does end of time interval occur before dest reached or fuel runs out?
        if dt < tAccel:
            # Time interval used up
            return (self.distanceTraveled(dt, v0, a),  # dist traveled during interval
                    self.velocity(dt, v0, a),  # velocity at end of interval
                    qFuel - self.fuelConsumed(dt),  # fuel remaining 
                    0.0,  # entire interval used
                    self.INTERVAL_END  # dest not reached yet
                   )
        
        # Did ship stop or reverse, or run out of fuel first?
        if tAccel == tStop:
            # Flight will never reach destination
            return (self.distanceTraveled(tAccel, v0, a),  # forward progress made
                    0.0,  # ship stopped
                    0.0,  # no fuel remaining
                    dt - tStop,  # time remaining after ship stopped
                    self.INTERVAL_DNF  # dest will not be reached
                   )
        
        # Fuel runs out, continue at constant velocity
        constVelocityInterval = self.computeNoThrustTravelInterval(dt - tAccel,  # time remaining after acceleration
                                                                   self.velocity(tAccel, v0, a),  # velocity after acceleration
                                                                   distToDest - self.distanceTraveled(tAccel, v0, a),  # dist remaining after acceleration
                                                                   0.0 # all fuel was used up
                                                                  )
        return (self.distanceTraveled(tAccel, v0, a) + constVelocityInterval[0],  # total dist after both phases
                constVelocityInterval[1],  # final velocity is passed through
                constVelocityInterval[2],  # final fuel quantity is passed through (0.0)
                constVelocityInterval[3],  # whatever is left after constV phase
                constVelocityInterval[4]   # final state is state at end of constV phase
               )
        
#         # Compute time to destination, assuming acceleration is constant
#         # over the entire distance
#         tDest = self.timeToTravel(distToDest, v0, a)  !!! gets an exception if velocity goes negative during the acceleration and can't compute a finite tDest
#         if tDest is None:
#             return (0.0, 0.0, qFuel, dt)
#         elif tDest < 0.0 and tDest < dt:
#             tDest = -tDest
#             return(self.distanceTraveled(tDest, v0, a),  # distance traveled before v goes to 0
#                    0.0,  # v goes to 0
#                    qFuel - self.fuelConsumed(tDest),  # fuel consumed before v goes to 0
#                    dt - tDest,  # time left
#                   )
#         
#         if a == 0.0:
#             # This is the simple, constant velocity case
#             if dt < tDest:
#                 # Dest is not reached during this time interval
#                 return (self.distanceTraveled(dt, v0, a),  # how far traveled in dt
#                         v0,  # velocity unchanged because a == 0
#                         qFuel,  # no fuel used, because a == 0   
#                         0.0,  # no time left in the interval
#                        )
#         else:
#             # If accelerating or decelerating, compute time until OutOfFuel
#             # at the given acceleration
#             tOutOfFuel = qFuel/self.rFuel  # amount of fuel/rate of consumption
#         
#             # Figure out if fuel runs out during the interval
#             if tDest <= dt and tDest <= tOutOfFuel:
#                 # Dest reached before running out of fuel or reaching end of interval dt
#                 return (distToDest,  # the entire distance to the destination was traversed
#                         self.velocity(tDest, v0, a),  # constant acceleration until dest reached
#                         max(0.0, qFuel - self.fuelConsumed(tDest)),  # amount of fuel remaining
#                         dt - tDest,  # some time is left over
#                        )
#             elif dt < tDest and dt <= tOutOfFuel:
#                 # End of time interval reached before running out of fuel or reaching dest
#                 return (self.distanceTraveled(dt, v0, a),  # how far traveled in dt
#                         self.velocity(dt, v0, a),  # constant acceleration for dt
#                         max(0.0, qFuel - self.fuelConsumed(tDest)),  # amount of fuel remaining
#                         0.0,  # no time left in the interval
#                        )
#             else:
#                 # Out of fuel while accelerating (or decelerating)
#                 dOutOfFuel = self.distanceTraveled(tOutOfFuel, v0, a)  # distance traveled during burn
#                 vOutOfFuel = self.velocity(tOutOfFuel, v0, a),  # final v is v when fuel runs out 
#                 (dCoast,_,_,tCoast) = self.computeTravelInterval(dt=dt - tOutOfFuel,
#                                                                     v0=vOutOfFuel,
#                                                                     a=0.0,
#                                                                     distToDest=distToDest - dOutOfFuel,
#                                                                     qFuel=0.0,  # fuel is all used up
#                                                                    )
#                 return (dOutOfFuel + dCoast,
#                         vOutOfFuel,
#                         0.0,  # no fuel remaining
#                         dt - tOutOfFuel - tCoast,
#                        )
         
    def currPhase(self, t):
        """ Return the flight phase for time t. """
        if   t <= 0.0: return self.START_PHASE
        elif t <= self.tAft: return self.ACCEL_PHASE
        elif t <= self.tAft + self.tCoast: return self.COAST_PHASE
        elif t <= self.tAft + self.tCoast + self.tFore: return self.DECEL_PHASE
        else: return self.GLIDE_PHASE

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
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelRemaining, tEnd)
        """
        phase = self.nextPhase(stateVec.phase)
        accel = self.acceleration(phase)
        dt = t - stateVec.tEnd  # time delta between end of last phase and t
        distRemaining = self.dist - stateVec.distTraveled
        
        d,v,fuelRemaining,tRemaining,intervalStatus = self.computeTravelInterval(dt, stateVec.currVelocity, accel, distRemaining, stateVec.fuelRemaining)
        
# #         if d + stateVec.distTraveled > self.dist: # went past the destination
# #             # Did we run out of fuel?
# #             if fuelRemaining <= 0.0: # then we ran out
# #                 # Did we run out before we reached the destination?
# #                 # Then compute the solution in two parts: the accelerated part and the constant velocity part
# #                 pass
# #             else:
# #                 # Compute time to reach dest
# #                 dt = self.timeToTravel(self.dist - stateVec.distTraveled, stateVec.currVelocity, accel)
# #                 d,v,fuelRemaining,tRemaining = self.computeTravelInterval(dt, stateVec.currVelocity, accel, distRemaining, stateVec.fuelRemaining)
# #                 phase = self.END_PHASE
#                 
#         if d >= distRemaining: # dest was reached
#             phase = self.END_PHASE
#             dt -= tRemaining
#             
# #         fuelRemaining = self.qFuel - (stateVec.fuelConsumed + fuelConsumed)
# #         return StateVec(phase, d + stateVec.distTraveled, v, stateVec.fuelConsumed + fuelConsumed, fuelRemaining, stateVec.tEnd + dt)

        endTime = stateVec.tEnd + dt - tRemaining
#         phase = self.currPhase(endTime)
        
        if intervalStatus in (self.INTERVAL_DNF, self.INTERVAL_DEST):
            phase = self.END_PHASE

        return StateVec(phase, d + stateVec.distTraveled, v, fuelRemaining, endTime)
    
    def computeAccelPhase(self, t, stateVec):
        """ Computes a state vector for an acceleration phase of time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelRemaining, tEnd)
        """
        return self.computePhase(t, stateVec)
    
    def computeCoastPhase(self, t, stateVec):
        """ Computes a state vector for the coast phase at time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelRemaining, tEnd)
        """
        return self.computePhase(t, stateVec)
        
    def computeDecelPhase(self, t, stateVec):
        """ Computes a state vector for the deceleration phase at time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelRemaining, tEnd)
        """
        return self.computePhase(t, stateVec)

    def computeGlidePhase(self, t, stateVec):
        """ Computes a state vector for the glide phase at time t.
            t is time in seconds since the start of the maneuver.
            Returns a StateVec containing (phase, distTraveled, currVelocity, fuelRemaining, tEnd)
        """
        return self.computePhase(t, stateVec)
        
    def flightDuration(self):
        """ Return the total duration of the docking maneuver.
            Return None if the terminal velocity is < 0.
        """
#         # Create initial stateVec
#         stateVec = StateVec(phase=self.START_PHASE,
#                             distTraveled=0.0,
#                             currVelocity=self.v0,
#                             fuelRemaining=self.qFuel,
#                             tEnd=0.0)
# 
#         # Walk through the individual simulation phases
#         stateVec = self.computeAccelPhase(self.tAft, stateVec)
#         if stateVec.phase == self.END_PHASE:
#             # Capsule reached port during acceleration phase
#             tEnd = stateVec.tEnd
#         else:
#             stateVec = self.computeCoastPhase(self.tAft + self.tCoast, stateVec)
#             if stateVec.phase == self.END_PHASE:
#                 # Capsule reached port during coast phase
#                 tEnd = stateVec.tEnd
#             else:
#                 stateVec = self.computeDecelPhase(self.tAft + self.tCoast + self.tFore, stateVec)
#                 if stateVec.phase == self.END_PHASE:
#                     # Capsule reached port during deceleration phase
#                     tEnd = stateVec.tEnd
#                 else:
#                     t = self.timeToTravel(self.dist - stateVec.distTraveled, stateVec.currVelocity, 0.0)
#                     if t is not None:
#                         # Capsule reached port during glide phase
#                         tEnd = stateVec.tEnd + t
#                     else:
#                         tEnd = None

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

        phaseTimes = [self.tAft, self.tAft + self.tCoast, self.tAft + self.tCoast + self.tFore]
        while stateVec.phase != self.END_PHASE:
            if phaseTimes and t > phaseTimes[0]:
                stateVec = self.computePhase(phaseTimes[0], stateVec)
                phaseTimes = phaseTimes[1:]
            else:
                # Compute the final time segment
                stateVec = self.computePhase(t, stateVec)
                break
            
#         # Walk through the individual simulation phases
#         if t < self.tAft:
#             stateVec = self.computeAccelPhase(t, stateVec)
#         else:
#             stateVec = self.computeAccelPhase(self.tAft, stateVec)
#             if stateVec.phase != self.END_PHASE:
#                 if (t - self.tAft) < self.tCoast:
#                     stateVec = self.computeCoastPhase(t, stateVec)
#                 else:
#                     stateVec = self.computeCoastPhase(self.tAft + self.tCoast, stateVec)
#                     if stateVec.phase != self.END_PHASE:
#                         if (t - self.tAft - self.tCoast) < self.tFore:
#                             stateVec = self.computeDecelPhase(t, stateVec)
#                         else:
#                             stateVec = self.computeDecelPhase(self.tAft + self.tCoast + self.tFore, stateVec)
#                             if stateVec.phase != self.END_PHASE:
#                                 stateVec = self.computeGlidePhase(t, stateVec)
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
