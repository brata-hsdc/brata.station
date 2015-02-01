import pibrella

#turn on the light sensor
pibrella.output.h.on()


#loop until the button is pressed
while pibrella.button.read() != 1:

	if pibrella.input.d.read() == 1:
		
		#turn on the lights if the sensor reads that 
		#the light is on			
		pibrella.light.red.on()
		pibrella.light.yellow.on()
		pibrella.light.green.on()

	else:
	
		#turn off the lights if the sensor does not
		#read that the light is on
		pibrella.light.red.off()
		pibrella.light.yellow.off()
		pibrella.light.green.off()

#turn off the lights before returning
pibrella.light.red.off()
pibrella.light.yellow.off()
pibrella.light.green.off()
