#!/usr/bin/python
#
#   File: FlightService.py
# Author: Ellery Chan
#  Email: ellery@precisionlightworks.com
#   Date: Jan 28, 2016
#
# Usage:
#
#----------------------------------------------------------------------------
from __future__ import print_function, division

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
#         params = cgi.FieldStorage(environ["wsgi.input"], environ=environ)
        params = json.loads(environ["wsgi.input"].read())
        print(repr(params))
        fp = FlightParams(tAft=params["t_aft"],
                          tCoast=params["t_coast"],
                          tFore=params["t_fore"],
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
#         
#         resp = "dockIsSuccessful: {}".format(ds.dockIsSuccessful())
#         resp += "terminalVelocity: {}".format(ds.terminalVelocity())
#         resp += "flightDuration: {}".format(ds.flightDuration())
#         resp += "StateVec: {}".format(ds.shipState(ds.flightDuration()))

        start_response("200 OK", [("Content-type", "text/plain")])
        resp = "You did not pass" #dockSim.result()
        yield resp.encode("utf-8")
    

#----------------------------------------------------------------------------
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    
    httpd = make_server("", 8080, wsgiApp)
    print("Serving on port 8080...")
    httpd.serve_forever()
