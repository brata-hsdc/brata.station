#!/usr/bin/python

import pibrella
import time

#turn on the light sensor
pibrella.output.h.on()

# INPUTS
stoprange = [2, 5]    # minimum and maximum number of stop gaps between symbols
nsymbols = 4          # number of symbols in the code
pulserange = [0.200*0.8, 0.250*1.2] # acceptable pulsewidth range
secure_timeout = 30.0 # timeout in seconds
secure_code = []      # expected secure code
maxcount = 7          # maximum symbol value

# LOCALS
light_on = 0          # Has the light (pulse) already been on
count = 0             # count of the current symbol

scount = 0            # count of the number of symbols
pulse_start = 0       # Pulse leading edge counter.
t1 = 0                # Time of pulse 1 leading edge
t2 = 0                # Time of pulse 2 leading edge
pulse_period = 0      # pulse period
pulse_width = 0       # pulse width
stime = time.time()   # start time
ctime = 0             # current time
ttime = 0             # trailing time
code = []             # the transmitted code

# return info
ERROR = 0             # error flag

def parse_secure_error(argument):
    switcher = {
        0: "passed",
        1: "Timeout",
        2: "Pulse width too small",
        4: "Pulse width too large",
        8: "Symbol too long or stop gap too small",
        16: "Stop gap too large"
        
    }
    return switcher.get(argument, "nothing")

print "Read in a code transmitted via light in a pulse train"
#loop until the number of symbols in a word are received
while (pibrella.button.read() != 1 and scount<nsymbols):
        # check if an error has occured
        if (ERROR):
                break
        # check if we need to timeout because of inactivity
        if ((time.time() - stime) > secure_timeout):
                ERROR = ERROR + 1
                break
        # Read pibrella inputs and do something for on or off
	if pibrella.input.d.read() == 1:
		# Trigger at the leading edge of the pulse
		if light_on == 0:
                        if pulse_start == 0:
                                t1 = time.time()
                        elif pulse_start == 1:
                                t2 = time.time()
                                pulse_period = t2 - t1 # time between first two pulses
                                pulse_width = pulse_period/2.0
                                # check pulse width size
                                if (pulse_width < pulserange[0]):
                                        #print "Pulse width %f ms" % (pulse_width*1000)
                                        ERROR = ERROR + 2
                                elif (pulse_width > pulserange[1]):
                                        ERROR = ERROR + 4
                                        #print "Pulse width %f ms" % (pulse_width*1000)
                        else:
                                count = count + 1
                        light_on = 1
                        pulse_start = pulse_start + 1
                        # print "pulse start %d" % pulse_start

	else:
                # get the current time
                ctime = time.time()
                # trailing edge of pulse
                if light_on == 1:
                        light_on = 0
                        ttime = ctime # time of trailing edge

                else:
                        # check to make sure we read the first two pulses
                        if (pulse_start >= 2):                              
                                # if off time is greater than the number of stop bits
                                if ((ctime-ttime) > (pulse_width*stoprange[0]+pulse_width)):
                                        #print "stop gap = %f ms" % ((ctime-ttime)*1000)
                                        #print "stoprange = %f ms" % (pulse_width*stoprange[0]*1000)
                                        # print "The Pulse count is %d" % count
                                        # error if the symbol is out of range
                                        if count > maxcount:
                                                ERROR = ERROR + 8
					code.append(count) # convert to char
                                        count = 0
                                        pulse_start = 0
					scount = scount + 1
			else:
                                # check if stop gap is too large
                                if (scount > 0):
                                        if (ctime-ttime) > (pulse_width*stoprange[1]+pulse_width):
                                                ERROR = ERROR + 16


if ERROR:
        print "Error: " + parse_secure_error(ERROR)
else:

        print "The code is " + ''.join(chr(i+48) for i in code).strip('[]')
        print "The period is %f ms" % (pulse_period*1000.0)
        print "The pulse width is %f ms" % (pulse_period/2*1000.0)
