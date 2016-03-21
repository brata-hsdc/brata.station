#!/bin/bash

# Display a screenful of text
#
# Usage: show_text.sh 'Multi-line|Text' [duration_s [COLOR [size [(x,y)]]]]
#
# duration_s  defaults to 10 sec.
# COLOR       must be WHITE, BLACK, RED, GREEN, BLUE, YELLOW,
#                CYAN, MAGENTA, ORANGE, LIGHT_ORANGE; defaults to WHITE
# size        is the height of a capital letter in pixels; defaults to 100
# (x,y)       is the position of the center of the text; defaults to (960,500)

station_addr=http://localhost:5000/rpi/start_challenge

# Get command line args
text=$1
duration_s=${2:-10}
color=${3:-WHITE}
size=${4:-100}
pos=${5:-(960,540)}

# Send message to display the text, then wait for the specified duration
http --json POST $station_addr Content-type:application/json Accept:application/json kiosk_text="(($size, Colors.$color, $pos, Text.CENTER|Text.MIDDLE, \'$text\'),)" > /dev/null
sleep $duration_s
