from datetime import datetime
import time
import random
import pibrella


#turn on the light sensor
pibrella.output.h.on()

#declare & initilize variables
count = 0
current_value = 0
value = 0
avg = 0
total = 0
i = 0


while True:

	current_value = pibrella.input.d.read()

	if current_value != value:
		if current_value == 1:
			print datetime.utcnow().strftime('%S.%f')[:-3] + ": light on!!!"
			ontime = datetime.utcnow()
		else:
			count = count + 1
			diff = datetime.utcnow() - ontime
			total = total + (diff.microseconds / 1000)
			avg = total / count
			print datetime.utcnow().strftime('%S.%f')[:-3] + ": light off!! Count = " + str(count) + " avg = " + str(avg)

		value = current_value
