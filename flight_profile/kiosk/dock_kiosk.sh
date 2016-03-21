#!/bin/bash
#
# File: dock_kiosk.sh
#
# Run Flight Profile simulations forever (Ctl-C to quit)
#   Alternate commands from multiple queue files

simTime=5
startSleep=10
simSleep=$(($simTime + 10))
resetSleep=3

# Commands used
station_ws=/opt/designchallenge2016/brata.station
kiosk=$station_ws/flight_profile/kiosk
get_next=$kiosk/get_next
show_text=$kiosk/show_text.sh
show_flight=$kiosk/show_flight.sh

echo -n "Starting wiremock... "
java -jar /opt/wiremock/wiremock-1.48-standalone.jar --root-dir /opt/designchallenge2016/brata.station/wiremock --no-request-journal >/dev/null 2>&1 &
wiremock_pid=$!
trap "kill -9 $wiremock_pid $$" 2
sleep 10
echo $wiremock_pid

echo -n "Starting Dock station... "
#DISPLAY=:0.0 python /opt/designchallenge2016/brata.station/bin/runstation -n dock01 &
DISPLAY=:0.0 python /opt/designchallenge2016/brata.station/bin/runstation -n dock01 >/dev/null 2>&1 &
runstation_pid=$!
trap "kill -9 $wiremock_pid $runstation_pid $$" 2
sleep 6
echo $runstation_pid

# Loop through kiosk screens until Ctrl-C
while true; do
   cmd=`$get_next $kiosk/text_screens`
   echo $cmd
   eval $cmd
   cmd=`$get_next $kiosk/flight_screens`
   echo $cmd
   eval $cmd
done
