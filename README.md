This document provides a quick description of how to build, install, and
run the application. Refer to the RaspberryPiGub page on the project wiki
for instructions on setting up hardware and a build environment prior to
proceeding with this document.

#---
# Build
#---

This is a Python application. So far, there is nothing to build.

#---
# Install
#---

Start by following the install for the master server up to but not including the
"Install Python dev to enable mod_wsgi install" section. 
TODO if we don't end up putting QR Codes in the station display for dock setup of the pi can stop after git is installed.

```sh
$ sudo raspi-config
```
go to advanced enable I2C
Finish which will restart

```sh
$ sudo pip install pibrella
$ sudo pip install mido
$ sudo pip install enum
$ sudo pip install python-dbus
$ sudo pi install Flask
$ sudo pip install tornado
$ sudo apt-get install build-essential python-dev python-smbus python-pip
$ cd ~
$ git clone https://github.com/adafruit/Adafruit_Python_CharLCD.git
$ cd Adafruit_Python_CharLCD
$ sudo python setup.py install
$ sudo mkdir /opt/designchallenge2015
$ cd /opt/designchallenge2015
$ sudo git clone https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code
```

You should be able to set this up on a Raspberry Pi station by following
the steps in the Pi Setup document. To get the code from the repository
into a standard location, run the following
```sh
$ sudo mkdir /opt/designchallenge2016
$ sudo chown pi:pi /opt/designchallenge2016
$ cd /opt/designchallenge2016
$ git clone https://github.com/brata-hsdc/brata.station.git
```

#---
# Run
#---
NOTE stations require secific hw for this year
return needs an adafruit 16x2 LCC color display
dock needs a Pi 2 and monitor that supports 1080p
secure requires the pibrella running the light sensor hw from 2015 cpa as well as an audio cable(s) that can direct the speaker output of the py to the mic input of an android phone 
To run a station: 
```sh
$ cd /opt/desognchallenge2016/brata.station/bin/
$ ./runstation -m ipofmasterserver:port -n stationname -t type
```

To run unit tests:
```sh
$ cd /opt/designchallenge2016/brata.station/sve/bin
$ ./runtests
```
To run the SVE application for the HMB:

   $ cd /opt/designchallenge2016/brata.station/sve/bin
   $ ./sve

To monitor SVE log output in another terminal window:

   $ tail -f /var/log/syslog

To mock the MS, see the README.txt file in the wiremock subdirectory.


TODO. This document needs to be written.

Random thoughts: This started as just a single application for the
HMB Raspberry Pi unit; however, current thoughts are on combining
it with the other station(s) into a single application. Let's see
if this works.

Unless someone has a reason not to, we can run Python with the -B option so the directory doesn't get cluttered with *.pyc files.

If you run this on your Pi, you shouldn't see any output on the command line.

Open a terminal window and keep it open. In that window, type the following before running the application:

   tail -f /var/log/syslog

When you run the application, you should see something like this in the window you're running tail:

Sep 14 20:51:45 raspberrypi Constructing SVE config
Sep 14 20:51:45 raspberrypi Constructing vibration motor Huey config
Sep 14 20:51:45 raspberrypi Constructing vibration motor Dewey config
Sep 14 20:51:45 raspberrypi Constructing vibration motor Louie config
Sep 14 20:51:45 raspberrypi Constructing LED red config
Sep 14 20:51:45 raspberrypi Constructing LED yellow config
Sep 14 20:51:45 raspberrypi Constructing LED green config
Sep 14 20:51:45 raspberrypi Constructing SVE
Sep 14 20:51:45 raspberrypi Constructing vibration manager Huey
Sep 14 20:51:45 raspberrypi Constructing vibration manager Dewey
Sep 14 20:51:45 raspberrypi Constructing vibration manager Louie
Sep 14 20:51:45 raspberrypi Constructing LED red
Sep 14 20:51:45 raspberrypi Constructing LED yellow
Sep 14 20:51:45 raspberrypi Constructing LED green
Sep 14 20:51:45 raspberrypi Starting SVE.

Then, back in the window that you ran SVE, press Ctrl+C. Now in your tail window, you should see:

Sep 14 20:52:35 raspberrypi Received signal "2". Stopping SVE.
Sep 14 20:52:35 raspberrypi Stopping vibration manager Huey
Sep 14 20:52:35 raspberrypi Stopping vibration manager Dewey
Sep 14 20:52:35 raspberrypi Stopping vibration manager Louie

As you keep rerunning the application, you'll see this output in the tail window; you shouldn't see anything in the window in which you run the "sve" script.

I've disabled everything regarding the push buttons, but the code is still in there. We'll need to clean it up some time after it gets into the repository.

The Pibrella code we used the other day still needs to be put into hw.py.
