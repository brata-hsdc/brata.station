#!/bin/bash
#
# Run Flight Profile simulations forever (Ctl-C to quit)

startSleep=10
simSleep=15
resetSleep=5

java -jar /opt/wiremock/wiremock-1.48-standalone.jar --root-dir /opt/designchallenge2016/brata.station/wiremock --no-request-journal &
wiremock_pid=$!
trap "kill -9 $wiremock_pid $$" 2
sleep 10
DISPLAY=:0.0 python /opt/designchallenge2016/brata.station/bin/runstation -n dock01 &
runstation_pid=$!
trap "kill -9 $wiremock_pid $runstation_pid $$" 2

sleep 10

while true; do

   echo "Send start_challenge"
   http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Space Team"
   sleep $startSleep
   echo "Send post_challenge (success)"
   http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='8.2' t_coast='1' t_fore='13.1' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='20' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim='5'
   sleep $simSleep
   http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   sleep $resetSleep
   
   echo "Send start_challenge"
   http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Space Racers"
   sleep $startSleep
   echo "Send post_challenge (too fast)"
   http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='10.2' t_coast='1' t_fore='13.1' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='20' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim='5'
   sleep $simSleep
   http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   sleep $resetSleep
   
   echo "Send start_challenge"
   http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Snail Space Team"
   sleep $startSleep
   echo "Send post_challenge (too slow)"
   http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='8.2' t_coast='1' t_fore='13.6' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='20' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim='5'
   sleep $simSleep
   http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   sleep $resetSleep
   
   echo "Send start_challenge"
   http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Hydrazine Hogs"
   sleep $startSleep
   echo "Send post_challenge (out of fuel in accel phase)"
   http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='8.2' t_coast='1' t_fore='13.1' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='5' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim='5'
   sleep $simSleep
   http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   sleep $resetSleep
   
   echo "Send start_challenge"
   http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Retro Rockettes"
   sleep $startSleep
   echo "Send post_challenge (reverse)"
   http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='2' t_coast='1' t_fore='13.1' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='20' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim='5'
   sleep $simSleep
   http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   sleep $resetSleep
   
   echo "Send start_challenge"
   http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Team Whose Name Takes Up a Lot of Space"
   sleep $startSleep
   echo "Send post_challenge (out of fuel in decel phase - success)"
   http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='3' t_coast='8' t_fore='13.1' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='5' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim='5'
   sleep $simSleep
   http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   sleep $resetSleep

   echo "Send start_challenge"
   http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Open the Pod Bay Doors Please, HAL"
   sleep $startSleep
   echo "Send post_challenge (out of fuel in decel phase - fail)"
   http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='4' t_coast='12' t_fore='13.1' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='5' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim='5'
   sleep $simSleep
   http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   sleep $resetSleep

   echo "Send start_challenge"
   http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Team Whose Name is Designed Solely to Test the Limits of the Font Scaling Feature Built into This Screen Layout Function"
   sleep $startSleep
   echo "Send post_challenge (out of fuel in decel phase - fail)"
   http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='4' t_coast='12' t_fore='13.1' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='5' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim='5'
   sleep $simSleep
   http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   sleep $resetSleep
   
   echo "Send start_challenge"
   http --json POST http://localhost:5000/rpi/start_challenge Content-type:application/json Accept:application/json team_name="Team Whose Name is Designed Solely to Test the Limits of the Automatic Font Scaling Feature Built into This Screen Layout Function, Whose Purpose is to Make Sure the Team Name Fits on the Screen Without Getting Clipped"
   sleep $startSleep
   echo "Send post_challenge (tiny accel)"
   http --json POST http://localhost:5000/rpi/post_challenge Content-type:application/json Accept:application/json t_aft='0.1' t_coast='0' t_fore='0' a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='20' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim='5'
   sleep $simSleep
   http --json GET http://localhost:5000/rpi/reset/31415 Content-type:text/html
   sleep $resetSleep

done