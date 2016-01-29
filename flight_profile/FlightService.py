#!/usr/bin/python
#
#   File: FlightService.py
# Author: Ellery Chan
#  Email: ellery@precisionlightworks.com
#   Date: Jan 28, 2016
#
# Usage:
#         python FlightService.py
#  then from another host:
#         http --json POST http://localhost:8080/dockparams Content-type:application/json Accept:text/plain t_aft=0.1 t_coast=1 t_fore=13.1
#
#----------------------------------------------------------------------------
from __future__ import print_function, division

import sys
import cgi
import json
from DockSim import DockSim, FlightParams

#----------------------------------------------------------------------------
def wsgiApp(environ, start_response):
    method = environ["REQUEST_METHOD"].lower()  # GET or POST
    path = environ["PATH_INFO"]  # relative part of the URL
    if method != "post" or path != "/dockparams":
        start_response("404 Not Found", [("Content-type", "text/plain")])
        resp = "404 Not Found"
        yield resp.encode("utf-8")
    else:
        start_response("200 OK", [("Content-type", "text/plain")])

        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0
        
        request_body = environ['wsgi.input'].read(request_body_size)
        
        params = json.loads(request_body)
        
        fp = FlightParams(tAft=float(params["t_aft"]),
                          tCoast=float(params["t_coast"]),
                          tFore=float(params["t_fore"]),
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
         
        finalState = ds.shipState(DockSim.MAX_FLIGHT_DURATION_S)
#         resp = "dockIsSuccessful: {}\n".format(ds.dockIsSuccessful())
#         resp += "terminalVelocity: {}\n".format(ds.terminalVelocity())
#         resp += "flightDuration: {}\n".format(ds.flightDuration())
#         resp += "outcome: {}\n".format(ds.outcome(ds.shipState(ds.flightDuration())))
        finalState = ds.shipState(DockSim.MAX_FLIGHT_DURATION_S)
        resp = "dockIsSuccessful: {}\n".format(str(ds.outcome(finalState) == DockSim.OUTCOME_SUCCESS))
        resp += "terminalVelocity: {}\n".format(finalState.currVelocity)
        resp += "flightDuration: {}\n".format(finalState.tEnd)
        resp += "outcome: {}\n".format(ds.outcome(finalState))
        resp += "state: {}\n".format(finalState)
        yield resp.encode("utf-8")
    

#----------------------------------------------------------------------------
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    
    httpd = make_server("", 8080, wsgiApp)
    print("Serving on port 8080...")
    httpd.serve_forever()
