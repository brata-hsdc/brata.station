#!/bin/bash
#
# Run Flight Profile simulations forever (Ctl-C to quit)

simTime=5
startSleep=10
simSleep=$(($simTime + 10))
resetSleep=3

# Commands used
station_ws=/opt/designchallenge2016/brata.station
show_text=$station_ws/station/test/show_text.sh
run_flight=$station_ws/station/test/run_flight.sh

java -jar /opt/wiremock/wiremock-1.48-standalone.jar --root-dir /opt/designchallenge2016/brata.station/wiremock --no-request-journal &
wiremock_pid=$!
trap "kill -9 $wiremock_pid $$" 2
sleep 10
DISPLAY=:0.0 python /opt/designchallenge2016/brata.station/bin/runstation -n dock01 &
runstation_pid=$!
trap "kill -9 $wiremock_pid $runstation_pid $$" 2

sleep 6

while true; do
   # echo "Send start_challenge"
   # http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json kiosk_text='((100, Colors.WHITE, (960,100), Text.CENTER|Text.MIDDLE, "Welcome\\nto the 2016"),(200, Colors.RED, (960,500), Text.CENTER|Text.MIDDLE, "HARRIS\\nDesign\\nChallenge"))'
   # sleep 5
   $show_text 'Welcome|to the 2016|Harris|Design|Challenge' 5 RED 200

   # echo "Send start_challenge"
   # http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json kiosk_text='((70, Colors.ORANGE, (960,300), Text.CENTER|Text.MIDDLE, "This monitor is displaying sample runs of\\nthe Docking Simulation that is one\\nof the four challenges the teams must\\npass during the competition.\\n \\nGood luck, teams!!"),)'
   # sleep 10
   $show_text 'This monitor is displaying sample runs of|the Docking Simulation that is one|of the four challenges the teams must|pass during the competition.||Good luck, teams!!' 10 ORANGE 70

   # echo "Send start_challenge"
   # http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Space Team"
   # sleep $startSleep
   # echo "Send post_challenge (success)"
   # http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='8.2' t_coast='1' t_fore='13.1' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='20' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim="$simTime"
   # sleep $simSleep
   # http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   # sleep $resetSleep
   $run_flight 8.2 1 13.1 'Space Team' $simTime
   
   # echo "Send start_challenge"
   # http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json kiosk_text='((100, Colors.ORANGE, (960,540), Text.CENTER|Text.MIDDLE, "This next one will fail"),)'
   # sleep 10
   $show_text 'This next one will fail' 10 ORANGE 100
   
   # echo "Send start_challenge"
   # http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Space Racers"
   # sleep $startSleep
   # echo "Send post_challenge (too fast)"
   # http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='10.2' t_coast='1' t_fore='13.1' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='20' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim="$simTime"
   # sleep $simSleep
   # http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   # sleep $resetSleep
   $run_flight 10.2 1 13.1 'Space Racers' $simTime
   
   # echo "Send start_challenge"
   # http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Snail Space Team"
   # sleep $startSleep
   # echo "Send post_challenge (too slow)"
   # http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='8.2' t_coast='1' t_fore='13.6' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='20' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim="$simTime"
   # sleep $simSleep
   # http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   # sleep $resetSleep
   $run_flight 8.2 1 13.6 'Snail Space Team' $simTime
   
   # echo "Send start_challenge"
   # http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Hydrazine Hogs"
   # sleep $startSleep
   # echo "Send post_challenge (out of fuel in accel phase)"
   # http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='8.2' t_coast='1' t_fore='13.1' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='5' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim="$simTime"
   # sleep $simSleep
   # http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   # sleep $resetSleep
   $run_flight 8.2 1 13.1 'Hydrazine Hogs' $simTime --q_fuel=5
   
   # echo "Send start_challenge"
   # http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Retro Rockettes"
   # sleep $startSleep
   # echo "Send post_challenge (reverse)"
   # http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='2' t_coast='45' t_fore='13.1' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='20' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim="$simTime"
   # sleep $simSleep
   # http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   # sleep $resetSleep
   $run_flight 2 45 13.1 'Retro Rockettes' $simTime
   
   # echo "Send start_challenge"
   # http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Team Whose Name Takes Up a Lot of Space"
   # sleep $startSleep
   # echo "Send post_challenge (out of fuel in decel phase - success)"
   # http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='3' t_coast='8' t_fore='13.1' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='5' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim="$simTime"
   # sleep $simSleep
   # http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   # sleep $resetSleep
   $run_flight 3 8 13.1 'Team Whose Name Takes Up a Lot of Space' $simTime --q_fuel=5

   # echo "Send start_challenge"
   # http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Open the Pod Bay Doors Please, HAL"
   # sleep $startSleep
   # echo "Send post_challenge (out of fuel in decel phase - fail)"
   # http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='4' t_coast='12' t_fore='13.1' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='5' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim="$simTime"
   # sleep $simSleep
   # http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   # sleep $resetSleep
   $run_flight 4 12 13.1 'Open the Pod Bay Doors Please, HAL' $simTime --q_fuel=5

   # echo "Send start_challenge"
   # http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Team Whose Name is Designed Solely to Test the Limits of the Font Scaling Feature Built into This Screen Layout Function"
   # sleep $startSleep
   # echo "Send post_challenge (out of fuel in decel phase - fail)"
   # http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='4' t_coast='12' t_fore='13.1' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='5' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim="$simTime"
   # sleep $simSleep
   # http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   # sleep $resetSleep
   $run_flight 4 12 13.1 'Team Whose Name is Designed Solely to Test the Limits of the Font Scaling Feature Built into This Screen Layout Function' $simTime --q_fuel=5
   
   # echo "Send start_challenge"
   # http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Team Whose Name is Designed Solely to Test the Limits of the Automatic Font Scaling Feature Built into This Screen Layout Function, Whose Purpose is to Make Sure the Team Name Fits on the Screen Without Getting Clipped"
   # sleep $startSleep
   # echo "Send post_challenge (tiny accel)"
   # http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='0.1' t_coast='0' t_fore='0' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='20' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim="$simTime"
   # sleep $simSleep
   # http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   # sleep $resetSleep
   $run_flight 0.1 0 0 'Team Whose Name is Designed Solely to Test the Limits of the Automatic Font Scaling Feature Built into This Screen Layout Function, Whose Purpose is to Make Sure the Team Name Fits on the Screen Without Getting Clipped' $simTime

done
