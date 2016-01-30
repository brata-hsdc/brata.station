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

responseHtml1 = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1  /DTD/xhtml1-strict.dtd">
<html>
<head>
  <title>Harris Design Challenge 2016 DOCK Simulation Results</title>
  <style type="text/css">
  body { font-family: Arial,Sans; }
  table td.label { text-align: right; font-weight: bold; }
  </style>
</head>
  
<body>
  <h3>Harris Design Challenge 2016 DOCK Simulation Results</h3>
  <form action="http://localhost:8080/dockparams" method="post">
    <div>
      <p>Enter your flight profile solution values here.</p>
      <table>
"""
responseHtml2 = """
        <tr><td class="label">Outcome:</td><td class="input"><input name="outcome" type="text" value="{}" /></td></tr>
        <tr><td class="label">Flight Duration (sec):</td><td class="input"><input name="duration" type="text" value="{}" /></td></tr>
        <tr><td class="label">Final Velocity (m/s):</td><td class="input"><input name="v_end" type="text" value="{}" /></td></tr>
        <tr><td class="label">Fuel Remaining (kg):</td><td class="input"><input name="q_fuel" type="text" value="{}" /></td></tr>
        <tr><td class="label">&nbsp;</td><td class="input">&nbsp;</td></tr>
        <tr><td class="label">&nbsp;</td><td class="input"><input type="button" onclick="history.back();" value="Try Again" /></td></tr>
      </table>
    </div>
  </form>
  <br />
  <p>The outcomes have the following meanings:</p>
  <table>
    <tr><td><b>OUTCOME_SUCCESS</b></td><td>The ship docked successfully (velocity within allowable range)</td></tr>
    <tr><td><b>OUTCOME_DNF</b></td><td>Did Not Finish because the velocity went to zero or went negative</td></tr>
    <tr><td><b>OUTCOME_NO_FUEL</b></td><td>The fuel ran out and the velocity was not in the acceptable range</td></tr>
    <tr><td><b>OUTCOME_TOO_FAST</b></td><td>The ship's docking velocity was too large</td></tr>
    <tr><td><b>OUTCOME_TOO_SLOW</b>&nbsp;&nbsp;</td><td>The ship's docking velocity was too small</td></tr>
  </table>
</body>
</html>
"""
responseText = """Outcome: {}
Flight Duration (sec): {}
Final Velocity (m/s): {}
Fuel Remaining (kg): {}
"""

#----------------------------------------------------------------------------
def wsgiApp(environ, start_response):
    """ Receive a request and dispatch to the correct handler """
    method = environ["REQUEST_METHOD"].lower()  # GET or POST
    path = environ["PATH_INFO"]  # relative part of the URL
    
    print("method", method, "  path", path)
    if method == "get" and path == "/dock":
        handle_dock(environ, start_response)
    elif method == "post" and path == "/dockparams":
            handle_dockparams(environ, start_response)
    else:
        handle_404(environ, start_response)

#     if method != "post" or path != "/dockparams":
#         start_response("404 Not Found", [("Content-type", "text/plain")])
#         resp = "404 Not Found"
#         yield resp.encode("utf-8")
#     else:
#         start_response("200 OK", [("Content-type", "text/html")])
# 
#         try:
#             request_body_size = int(environ.get('CONTENT_LENGTH', 0))
#         except ValueError:
#             request_body_size = 0
#         
#         if environ.get('CONTENT_TYPE') == "application/json":
#             request_body = environ['wsgi.input'].read(request_body_size)
#             params = json.loads(request_body)
#             fp = FlightParams(tAft=float(params["t_aft"] if "t_aft" in params else 0.0),
#                               tCoast=float(params["t_coast"] if "t_coast" in params else 0.0),
#                               tFore=float(params["t_fore"] if "t_fore" in params else 0.0),
#                               aAft=float(params["a_aft"] if "a_aft" in params else 0.15),
#                               aFore=float(params["a_fore"] if "a_fore" in params else 0.09),
#                               rFuel=float(params["r_fuel"] if "r_fuel" in params else 0.7),
#                               qFuel=float(params["q_fuel"] if "q_fuel" in params else 20.0),
#                               dist=float(params["dist"] if "dist" in params else 15.0),
#                               vMin=float(params["v_min"] if "v_min" in params else 0.01),
#                               vMax=float(params["v_max"] if "v_max" in params else 0.1),
#                               vInit=float(params["v_init"] if "v_init" in params else 0.0),
#                               tSim=int(params["t_sim"] if "t_sim" in params else 45),
#                              )
#         else: # CONTENT-TYPE == "x-www-form-urlencoded"
#             params = cgi.FieldStorage(environ['wsgi.input'], environ=environ)
#             fp = FlightParams(tAft=float(params["t_aft"].value if "t_aft" in params else 0.0),
#                               tCoast=float(params["t_coast"].value if "t_coast" in params else 0.0),
#                               tFore=float(params["t_fore"].value if "t_fore" in params else 0.0),
#                               aAft=float(params["a_aft"].value if "a_aft" in params else 0.15),
#                               aFore=float(params["a_fore"].value if "a_fore" in params else 0.09),
#                               rFuel=float(params["r_fuel"].value if "r_fuel" in params else 0.7),
#                               qFuel=float(params["q_fuel"].value if "q_fuel" in params else 20.0),
#                               dist=float(params["dist"].value if "dist" in params else 15.0),
#                               vMin=float(params["v_min"].value if "v_min" in params else 0.01),
#                               vMax=float(params["v_max"].value if "v_max" in params else 0.1),
#                               vInit=float(params["v_init"].value if "v_init" in params else 0.0),
#                               tSim=int(params["t_sim"].value if "t_sim" in params else 45),
#                              )
#         ds = DockSim(fp)
#          
#         finalState = ds.shipState(DockSim.MAX_FLIGHT_DURATION_S)
#         if "text/html" in environ.get("HTTP_ACCEPT"):
#             resp = responseHtml1 + \
#                    responseHtml2.format(ds.outcome(finalState), finalState.tEnd, finalState.currVelocity, finalState.fuelRemaining)
#         else: # fall back to plain text
#             resp = responseText.format(ds.outcome(finalState), finalState.tEnd, finalState.currVelocity, finalState.fuelRemaining)
#         yield resp.encode("utf-8")
    

#----------------------------------------------------------------------------
def handle_dock(environ, start_response):
    """ Return the web page form for the user to enter parameters """
    scriptDir = os.path.dirname(__file__)
    with open(os.path.join(scriptDir, "FlightService.html"), "r") as webForm:
        html = webForm.read()
    start_response("200 OK", [("Content-type", "text/html")])
    yield html.encode("utf-8")
    
#----------------------------------------------------------------------------
def handle_dockparams(environ, start_response):
    start_response("200 OK", [("Content-type", "text/html")])

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
    if "text/html" in environ.get("HTTP_ACCEPT"):
        resp = responseHtml1 + \
               responseHtml2.format(ds.outcome(finalState), finalState.tEnd, finalState.currVelocity, finalState.fuelRemaining)
    else: # fall back to plain text
        resp = responseText.format(ds.outcome(finalState), finalState.tEnd, finalState.currVelocity, finalState.fuelRemaining)
    yield resp.encode("utf-8")

#----------------------------------------------------------------------------
def handle_404(environ, start_response):
    start_response("404 Not Found x", [("Content-type", "text/plain")])
    resp = "404 Not Found y"
    yield resp.encode("utf-8")


#----------------------------------------------------------------------------
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    
    httpd = make_server("", 8080, wsgiApp)
    print("Serving on port 8080...")
    httpd.serve_forever()
