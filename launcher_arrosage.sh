#!/bin/sh
cd /home/pi/arrosage
python3 mqtt_subscribe.py &
python3 main.py & 
