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
import os.path

from DockSim import DockSim, FlightParams

REQUEST_FORM = "FlightService.html"
RESPONSE_FORM = "FlightServiceResult.html"
RESPONSE_TEXT = """Outcome: {}
Flight Duration (sec): {}
Final Velocity (m/s): {}
Fuel Remaining (kg): {}
"""

#----------------------------------------------------------------------------
def wsgiApp(environ, start_response):
    """ Receive a request and dispatch to the correct handler """
    method = environ["REQUEST_METHOD"]  # GET or POST
    path = environ["PATH_INFO"]  # relative part of the URL
    thisHost = environ["HTTP_HOST"]  # host used to request this page

    if method == "GET" and path == "/dock":
        return handle_dock(environ, start_response)
    elif method == "POST" and path == "/dockparams":
        return handle_dockparams(environ, start_response)
    else:
        return handle_404(environ, start_response)


#----------------------------------------------------------------------------
def handle_dock(environ, start_response):
    """ Return the web page form for the user to enter parameters """
    thisHost = environ["HTTP_HOST"]  # host used to request this page
    scriptDir = os.path.dirname(__file__)
    with open(os.path.join(scriptDir, REQUEST_FORM), "r") as webForm:
        html = webForm.read()
    html = html.replace("%FLIGHT_SERVICE_HOST%", thisHost)
    
    start_response("200 OK", [("Content-type", "text/html")])
    return html.encode("utf-8")
    
#----------------------------------------------------------------------------
def handle_dockparams(environ, start_response):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0
    
    if environ.get('CONTENT_TYPE') == "application/json":
        request_body = environ['wsgi.input'].read(request_body_size)
        params = json.loads(request_body)
        fp = FlightParams(tAft=float(params["t_aft"] if "t_aft" in params else 0.0),
                          tCoast=float(params["t_coast"] if "t_coast" in params else 0.0),
                          tFore=float(params["t_fore"] if "t_fore" in params else 0.0),
                          aAft=float(params["a_aft"] if "a_aft" in params else 0.15),
                          aFore=float(params["a_fore"] if "a_fore" in params else 0.09),
                          rFuel=float(params["r_fuel"] if "r_fuel" in params else 0.7),
                          qFuel=float(params["q_fuel"] if "q_fuel" in params else 20.0),
                          dist=float(params["dist"] if "dist" in params else 15.0),
                          vMin=float(params["v_min"] if "v_min" in params else 0.01),
                          vMax=float(params["v_max"] if "v_max" in params else 0.1),
                          vInit=float(params["v_init"] if "v_init" in params else 0.0),
                          tSim=int(params["t_sim"] if "t_sim" in params else 45),
                         )
    else: # CONTENT-TYPE == "x-www-form-urlencoded"
        params = cgi.FieldStorage(environ['wsgi.input'], environ=environ)
        fp = FlightParams(tAft=float(params["t_aft"].value if "t_aft" in params else 0.0),
                          tCoast=float(params["t_coast"].value if "t_coast" in params else 0.0),
                          tFore=float(params["t_fore"].value if "t_fore" in params else 0.0),
                          aAft=float(params["a_aft"].value if "a_aft" in params else 0.15),
                          aFore=float(params["a_fore"].value if "a_fore" in params else 0.09),
                          rFuel=float(params["r_fuel"].value if "r_fuel" in params else 0.7),
                          qFuel=float(params["q_fuel"].value if "q_fuel" in params else 20.0),
                          dist=float(params["dist"].value if "dist" in params else 15.0),
                          vMin=float(params["v_min"].value if "v_min" in params else 0.01),
                          vMax=float(params["v_max"].value if "v_max" in params else 0.1),
                          vInit=float(params["v_init"].value if "v_init" in params else 0.0),
                          tSim=int(params["t_sim"].value if "t_sim" in params else 45),
                         )
    ds = DockSim(fp)
    finalState = ds.shipState(DockSim.MAX_FLIGHT_DURATION_S)
    
    responseType = "text/html"
    if responseType in environ.get("HTTP_ACCEPT"):
        scriptDir = os.path.dirname(__file__)
        with open(os.path.join(scriptDir, RESPONSE_FORM), "r") as webForm:
            resp = webForm.read()
        thisHost = environ["HTTP_HOST"]  # host used to request this page
        resp = resp.replace("%FLIGHT_SERVICE_HOST%", thisHost)\
                   .replace("%OUTCOME%",  ds.outcome(finalState))\
                   .replace("%DURATION%", str(finalState.tEnd))\
                   .replace("%V_END%",    str(finalState.currVelocity))\
                   .replace("%Q_FUEL%",   str(finalState.fuelRemaining))
    else: # fall back to plain text
        responseType = "text/plain"
        resp = RESPONSE_TEXT.format(ds.outcome(finalState), finalState.tEnd, finalState.currVelocity, finalState.fuelRemaining)

    start_response("200 OK", [("Content-type", responseType)])
    return resp.encode("utf-8")

#----------------------------------------------------------------------------
def handle_404(environ, start_response):
    responseType = "text/html"
    if responseType in environ.get("HTTP_ACCEPT"):
        resp = """<html><head><title>404 Not Found</title></head>
<body>
404 Not Found<br />
Click <a href="http://{}/dock">here</a>, or<br />
check the URL of your request and try again.
</body></html>
""".format(environ["HTTP_HOST"])
    else:
        responseType = "text/plain"
        resp = "404 Not Found.\nCheck the URL of your request and try again."

    start_response("404 Not Found", [("Content-type", responseType)])
    return resp.encode("utf-8")


#----------------------------------------------------------------------------
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    
    httpd = make_server("", 8080, wsgiApp)
    print("Serving on port 8080...")
    httpd.serve_forever()
