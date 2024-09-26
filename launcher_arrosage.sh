#!/bin/sh
cd /home/pi/arrosage &&
python3 main.py &
python3 mqtt_subscribe.py &
python3 lcd.py &
python3 mqtt_diagnostic.py &
python3 maj_json.py &
python3 automation.py &
python3 weather.py &
