#!/usr/bin/PYTHON
"""
       File:  NetStatusMonitor.py
     Author:  Ellery Chan <ellery.chan@gmail.com>
       Date:  27 Feb 2015

Description:  Provides a status display window to monitor the network status of
              a group of machines.  Specifically, this is tailored to monitor
              the set of Raspberry Pi-based competition stations for the 2015
              Harris High School Design Challenge.  It shows a box for each
              station, displayed green if the station is responding to pings,
              otherwise red.
              
              The app uses TkInter to make the GUI.
              The app will probably need minor tweaks to run in Windows.
              
              The window is somewhat resizable.
              Etherape can also be run alongside this, with appropriate settings,
              to provide an entertaining dynamic display of the network activity.
              
              The IP addresses of the machines to be scanned are hard-coded in
              an array.
              
      Usage:  python NetStatusMonitor.py
"""

import subprocess

from Tkinter import *
import tkFont

class StatusGroup(Frame):
    """ A Frame with a label on the left and a row of buttons to the right. """
    def __init__(self, parent, groupName="group", numStations=6, fontSize=18):
        """ Constructor. """
        Frame.__init__(self, parent)
        self._groupName = groupName
        self._stations = []
        self._num = numStations
        self._fontSize = fontSize
        self._buttonFont = tkFont.Font(family="Helvetica", size=self._fontSize, weight="bold")
        self._labelFont = tkFont.Font(family="Helvetica", size=self._fontSize, weight="bold")
        self.create()
        
    def create(self):
        """ Create the child widgets for this element.
            
            TODO:  Find a better way to set the label width.  It is hard-coded
                   here at 6 chars, just to get stuff to look good.
        """
        lab = Label(self, text=self._groupName, width=6, font=self._labelFont)
        lab.pack(side="left")
        
        for i in range(self._num):
            b = Button(self, text="{:02}".format(i+1), font=self._buttonFont)
            self._stations.append(b)
            b.pack(side="left", expand=True, fill="both")
    
    def setStatus(self, statArray):
        """ Set the button color for each button based on an array of flags.
        
            statArray contains a status value for each element.  True turns
            the corresponding button green.  False turns it red.
            
            Note:  Could pass in an array of colors instead.
        """
        for s in zip(self._stations, statArray):
            s[0]["background"] = "green" if s[1] else "red"
            
class StatusWindow(Frame):
    """ The app main window, containing several StatusGroups. """
    def __init__(self, parent, title="StatusApp", fontSize=18):
        """ Constructor. """
        Frame.__init__(self, parent)
        self._title = title
        self._fontSize = fontSize
        self.create()
        
    def create(self):
        """ Create the status groups. """
        self.master.title(self._title)
        self._cpaStatus = StatusGroup(self, "CPA", numStations=6, fontSize=self._fontSize)
        self._cpaStatus.pack(expand=True, fill="both")
        self._ctsStatus = StatusGroup(self, "CTS", numStations=6, fontSize=self._fontSize)
        self._ctsStatus.pack(expand=True, fill="both")
        self._hmbStatus = StatusGroup(self, "HMB", numStations=6, fontSize=self._fontSize)
        self._hmbStatus.pack(expand=True, fill="both")
        self._msStatus = StatusGroup(self, "MS", numStations=1, fontSize=self._fontSize)
        self._msStatus.pack(expand=True, fill="both")
    
    def setStatus(self, status):
        """ Set the button statuses from an ordered array of flags. """
        self._cpaStatus.setStatus(status[0:6])
        self._ctsStatus.setStatus(status[6:12])
        self._hmbStatus.setStatus(status[12:18])
        self._msStatus.setStatus([status[18]])

class NetStatusMonitorApp():
    """ Make a window full of status indicators, and update them periodically.
        
        The app pings each IP address, records whether it gets a response, and
        displays the results.
    """
    def __init__(self):
        """ Constructor.
            
            The IP addresses are defined here
        """
        self._win = None
        self._ips = ["192.168.1.11", "192.168.1.12", "192.168.1.13", "192.168.1.14", "192.168.1.15", "192.168.1.16",  # CPA
                     "192.168.1.21", "192.168.1.22", "192.168.1.23", "192.168.1.24", "192.168.1.25", "192.168.1.26",  # CTS
                     "192.168.1.31", "192.168.1.32", "192.168.1.33", "192.168.1.34", "192.168.1.35", "192.168.1.36",  # HMB
                     "192.168.1.1",                                                                                   # MS
                    ]
        self._status = [0] * len(self._ips)  # A status flag for each IP
        self._count = 0  # Which IP to ping next
        
        self._tk = Tk()  # Initialize the Tk widgets
        self.create()
        
    def create(self):
        """ Create the app window. """
        self._win = StatusWindow(self._tk, title="Station Status", fontSize=24)
        self._win.pack(expand=True, fill="both")
    
    def update(self):
        """ Ping one IP address and update its status flag.
        
            _count indicates which IP to ping next.  Increment it and wrap it.
            _count is used to index into the _ips and _status arrays.
            
            This method is called by a one-shot timer from the Tk main loop, so
            it needs to set itself up again each time it is invoked.  It puts
            a 100 ms delay between calls, and a 1000 ms delay after each pass
            through all the _ips.
            
            TODO:  Delays should probably not be hard-coded here.
        """
        numIps = len(self._ips)
        self._count = (self._count + 1) % numIps
        self._status[self._count] = self.ping(self._ips[self._count])
        self._win.setStatus(self._status)
        self._tk.after(100 if self._count < (numIps-1) else 1000, self.update)
    
    def ping(self, ip):
        """ Call the system ping command, redirect its output to /dev/null, and get the status.
        
            TODO:  This is non-portable.  It will not work on Windows as-is.  Use NUL: and
                   the Windows version of ping.
        """
        with open("/dev/null", "w") as f:
            ret = subprocess.call(["/usr/bin/ping", "-q", "-n", "-c", "1", "-W", "1", ip], stdout=f, stderr=f)
        return ret == 0
        
    def run(self):
        """ Set the update service method to fire, and enter the main loop. """
        self._tk.after(10, self.update)
        self._tk.mainloop()

#--------------------------------------------------------
if __name__ == "__main__":
    app = NetStatusMonitorApp()  # Create the app object
    app.run()                 # Run the app
    