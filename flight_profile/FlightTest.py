#!/usr/bin/python
#
#   File: FlightTest.py
# Author: Ellery Chan
#  Email: ellery@precisionlightworks.com
#   Date: 5 Jan 2016
"""
Collect flight profile parameters and run a simulation.
"""
from __future__ import print_function, division

from Tkinter import Tk, LabelFrame, Label, Spinbox, Button, Checkbutton, IntVar, RIGHT, END
import sys
import os.path
import subprocess


#----------------------------------------------------------------------------
class FlightTestApp(object):
    """ A GUI for FlightProfile """
    def __init__(self):
        self.create()
        
    def create(self):
        self.root = Tk()
        self.root.title("Flight Test")
        
        self.root.grid_columnconfigure(1, weight=1)
        
        frame = LabelFrame(self.root, text="User Inputs", padx=5, pady=5)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid(row=0, column=0, sticky="NEWS", padx=5, pady=5)
        Label(frame, text="Acceleration Phase (sec):").grid(row=0, column=0, sticky="E")
        Label(frame, text="Coast Phase (sec):").grid(row=1, column=0, sticky="E")
        Label(frame, text="Deceleration Phase (sec):").grid(row=2, column=0, sticky="E")
        
        self.tAft = Spinbox(frame, from_=-1000.0, to=1000.0, width=6, increment=0.1, justify=RIGHT)
        self.tAft.grid(row=0, column=1, sticky="WE")
        self.tCoast = Spinbox(frame, from_=-1000.0, to=1000.0, width=6, increment=0.1, justify=RIGHT)
        self.tCoast.grid(row=1, column=1, sticky="WE")
        self.tFore = Spinbox(frame, from_=-1000.0, to=1000.0, width=6, increment=0.1, justify=RIGHT)
        self.tFore.grid(row=2, column=1, sticky="WE")
        
        frame = LabelFrame(self.root, text="Flight Params", padx=5, pady=5)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid(row=1, column=0, sticky="NEWS", padx=5, pady=5)
        Label(frame, text="Acceleration Force (m/s^2):").grid(row=0, column=0, sticky="E")
        Label(frame, text="Deceleration Force (m/s^2):").grid(row=1, column=0, sticky="E")
        Label(frame, text="Fuel Rate of Consumption (kg/s):").grid(row=2, column=0, sticky="E")
        Label(frame, text="Initial Fuel Amount (kg):").grid(row=3, column=0, sticky="E")
        Label(frame, text="Distance to Dock (m):").grid(row=4, column=0, sticky="E")
        
        self.aAft = Spinbox(frame, from_=-1000.0, to=1000.0, width=6, increment=0.1, justify=RIGHT)
        self.aAft.grid(row=0, column=1, sticky="WE")
        self.aFore = Spinbox(frame, from_=-1000.0, to=1000.0, width=6, increment=0.1, justify=RIGHT)
        self.aFore.grid(row=1, column=1, sticky="WE")
        self.rFuel = Spinbox(frame, from_=-1000.0, to=1000.0, width=6, increment=0.1, justify=RIGHT)
        self.rFuel.grid(row=2, column=1, sticky="WE")
        self.qFuel = Spinbox(frame, from_=-1000.0, to=1000.0, width=6, increment=0.1, justify=RIGHT)
        self.qFuel.grid(row=3, column=1, sticky="WE")
        self.dist = Spinbox(frame, from_=-1000.0, to=1000.0, width=6, increment=0.1, justify=RIGHT)
        self.dist.grid(row=4, column=1, sticky="WE")
        
        self.setValue(self.tAft, 8.2)
        self.setValue(self.tCoast, 1.0)
        self.setValue(self.tFore, 13.1)
        self.setValue(self.aAft, 0.15)
        self.setValue(self.aFore, 0.09)
        self.setValue(self.rFuel, 0.7)
        self.setValue(self.qFuel, 20.0)
        self.setValue(self.dist, 15.0)
        
        self.fullscreen = IntVar()
        Checkbutton(self.root, text="Fullscreen (1920 x 1080)", variable=self.fullscreen).grid(row=8, column=0, columnspan=2)

        Button(self.root, text=" Run Simulation ", command=self.runSim).grid(row=9, column=0, columnspan=2, sticky="WE", padx=5, pady=5)
        
        Label(self.root, text="(Press ESC to return to this window)").grid(row=10, column=0, columnspan=2, sticky="N")

    def setValue(self, widget, value):
        widget.delete(0, END)
        widget.insert(0, value)

    def runSim(self):
        scriptDir = os.path.dirname(__file__)

        cmd = ["python", os.path.join(scriptDir, "FlightProfile.py")]
        if self.fullscreen.get():
            cmd.append("--fullscreen")
        cmd.append("--tAft={}".format(self.tAft.get()))
        cmd.append("--tCoast={}".format(self.tCoast.get()))
        cmd.append("--tFore={}".format(self.tFore.get()))
        cmd.append("--aAft={}".format(self.aAft.get()))
        cmd.append("--aFore={}".format(self.aFore.get()))
        cmd.append("--rFuel={}".format(self.rFuel.get()))
        cmd.append("--qFuel={}".format(self.qFuel.get()))
        cmd.append("--dist={}".format(self.dist.get()))
        
        print("\nCmd: ", " ".join(cmd))
        subprocess.call(cmd)
            
    def run(self):
        self.root.mainloop()


#----------------------------------------------------------------------------
if __name__ == '__main__':
    app = FlightTestApp()
    app.run()
    sys.exit(0)
