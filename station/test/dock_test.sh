#!/bin/sh
startSleep=10
simSleep=15
resetSleep=5

DISPLAY=:0.0 python /opt/designchallenge2016/brata.station/bin/runstation -n dock01 &
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
   echo "Send post_challenge (out of fuel)"
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
done