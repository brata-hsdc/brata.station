#!/usr/bin/env python


import pibrella, signal

#while True:
#	pibrella.light.pulse(0,0,1,1)
	
	
#pibrella.exit()



#pibrella.light.pulse(0,0,1,1)	
# fade in, fade out, on time, off time
pibrella.output.e.pulse(0,0,1,2)
pibrella.output.f.pulse(0,0,1,3)
pibrella.output.g.pulse(0,0,1,5)
#pibrella.output.e.on()
pibrella.pause()
