#!/bin/bash

# Run a canned flight simulation
#
# Usage: show_flight.sh t_aft t_coast t_fore team_name [sim_duration]

station_addr=http://localhost:5000/rpi

# Simulation runtime (default 10 sec)
# and sleep times between sending the commands
sim_duration=${5:-10}
start_sleep_s=10
sim_sleep_s=$(($sim_duration + 10))
reset_sleep_s=3

# Command line args
t_aft=$1
t_coast=$2
t_fore=$3
team_name=${4:-Mystery Team}

# Send start_challenge:  go to Welcome screen
http --json POST $station_addr/start_challenge Content-type:application/json Accept:application/json team_name="$team_name" > /dev/null
sleep $start_sleep_s

# Send post_challenge:  run the sim, show the result
http --json POST $station_addr/post_challenge Content-type:application/json Accept:application/json t_aft="$t_aft" t_coast="$t_coast" t_fore="$t_fore" a_aft='.15' a_fore='0.09' r_fuel='0.7' q_fuel='20' dist='15.0' v_min='0.01' v_max='0.1' v_init='0.0' t_sim="$sim_duration" > /dev/null
sleep $sim_sleep_s

# Send reset:  go to Ready screen
#http --json GET $station_addr/reset/31415 Content-type:text/html > /dev/null
#sleep $reset_sleep_s
