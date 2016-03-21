# Kiosk Instructions

## Introduction

The Dock station can be used as a kiosk display.  It can run flight simulations repeatedly, and can also
display screens of text.  The kiosk display will run until terminated by a user.


## Running the kiosk display

To run the Dock station in kiosk mode:

```bash
./dock_kiosk.sh
```

This runs the `dock_kiosk.sh` script.  The script does the following:

1. Starts `wiremock` so the station thinks it is talking to a server.
2. Starts the station by invoking `runstation`.
3. Alternately reads commands from two files:
   a. flight_screens
   b. text_screens


## The *_screens command files

The files contain commands that call the `show_flight.sh` script or the `show_text.sh` script.
Multiple commands can be executed together by placing them on the same line.  `dock_kiosk.sh`
reads and executes one line at a time.  It ignores blank lines and comment lines.

The commands in the __*_screens__ files may use **$show_flight** and **$show_text** to invoke the
scripts.  The full script path is defined in `dock_kiosk.sh`.  Variable expansion is performed
on the commands read from the __*_screens__ files.


## show_flight.sh

Invoke `show_flight.sh` as follows:

```bash
# Usage: show_flight.sh t_aft t_coast t_fore team_name [sim_duration [welcome_duration [result_duration [reset_duration]]]]
```

## show_text.sh

Invoke `show_text.sh` as follows:

```bash
# Usage: show_text.sh 'Multi-line|Text' [duration_s [COLOR [size [(x,y)]]]]
#
# duration_s  defaults to 10 sec.
# COLOR       must be WHITE, BLACK, RED, GREEN, BLUE, YELLOW,
#                CYAN, MAGENTA, ORANGE, LIGHT_ORANGE; defaults to WHITE
# size        is the height of a capital letter in pixels; defaults to 100
# (x,y)       is the position of the center of the text; defaults to (960,540)
```

