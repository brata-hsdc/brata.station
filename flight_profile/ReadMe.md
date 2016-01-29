# Flight Profile Instructions

## Introduction

The *flight_profile* directory contains the following modules:

| **Module**        | **Description** |
| ----------------- | --------------- |
| **DockSim**       | Computes the simulation state given the flight parameters and the time |
| **FlightProfile** | Generates an animated graphical display of the simulation |
| **FlightTest**    | A simple GUI for running **FlightProfile** with different sets of flight parameters |
| **FlightService** | A REST service for testing sets of flight parameters from a web page |

**FlightProfile** uses *pygame* to generate sprite-based graphics.  The **FlightProfile** graphics are designed to run on an HD-resolution (1920x1080) display.


## Running FlightProfile

**FlightProfile** can be run from the command line like this:

```
cd /opt/designchallenge2016/brata.station
PYTHONPATH=/opt/designchallenge2016/brata.station; export PYTHONPATH
python flight_profile/FlightProfile.py --fullscreen --tAft=8.1 --tCoast=1.0 --tFore=13.1 --aAft=0.15 --aFore=0.09 --rFuel=0.7 --qFuel=20.0 --dist=15.0 --vMin=0.01 --vMax=0.1 --vInit=0.0 --tSim=5
```

Hit the **ESC** key to exit the graphical simulation.


## Running FlightTest

**FlightProfile** can be run from the **FlightTest** GUI, which makes entering and experimenting with the parameters easier, like this:

```
cd /opt/designchallenge2016/brata.station
PYTHONPATH=/opt/designchallenge2016/brata.station; export PYTHONPATH
python flight_profile/FlightTest.py
```

Then from the GUI, enter the parameter values you want, and click the Run Simulation button.  Hit the **ESC** key to exit the graphical simulation.


## Running FlightService

**FlightService** runs a simple HTTP server on port 8080.  You can either send it values with a utility like *curl* or *http*, or you can send it form data from a web page.

Start the service like this:

```
cd /opt/designchallenge2016/brata.station
python flight_profile/FlightService.py
```

To send a query from the command line, do this:

```
http --json POST http://localhost:8080/dockparams Content-type:application/json Accept:text/plain t_aft=0.1 t_coast=1 t_fore=13.1
```

Or use the **FlightService.html** web form to submit flight parameters and get a result back.

Note:  The **FlightService.html** page will have to be edited to insert the URL for the **FlightService**.  Replace *localhost* with the hostname or IP address of the server running **FlightService** in the following line:

```
  <form action="http://localhost:8080/dockparams" method="post">
```