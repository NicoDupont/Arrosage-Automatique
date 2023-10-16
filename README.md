# Arrosage Automatique

A raspberry pi project to automate my irrigation system mainly based on a raspberrypi and rain bird dv100 24vac solenoid valves  

Last Update : 16/10/2023  
This is the first working version for summer 2023, it will be adapted for 2024.

**Main Goal : replace one or more irrigation controllers and do it by mylself.**    

 **Big Concept :**

 - Logic is done by python scripts on the rpi
 - Data management is done with an sql data base, mqtt, json, yaml
 - UI is based on a web application or in Home Assistant
 - Sensors data comes from home-assistant/esphome

 **Overall functional descriptions :**

- A WebApp allows me to manage each solenoid valve/zone, global parameters, see the latest events, the watering sequence and some data.
- A collection of python scripts are used to open or close the solenoid valves and compute the watering sequence 
   - There is a winter/stop, test, , sequence on demande, automatic and domotic/manual mode
   - The program checks some data to know if it can run watering
   - Each change is logged
   - status are logged and send to an mqtt brocker
   - Errors and status are displayed on an lcd
   - The raspberry pi can run the irrigation without lan network and internet. In that case, json files are used for the configuration but it is impossible to change anything.
- config.yaml file is used to configure the script in addition with the database.
- I can bypass the programmation to directly power supply and open any solenoid valve I want with 3 positions switch wired for each solenoid valve.
- Monitoring and filling of the tank are managed by home assistant (see side projects)
- There is also a first implementation of mqtt to exchange data with home-assistant

**Folder organisation :**

	| IrriPi
	  => | App ( SqlDatabase and WebApp(php,html,css,js) )
	     | Doc    (img / Schematic / Diagram / Fritzing parts / Useful docs for the project )  
         | rpi (python scripts)
	     readme.md

**Raspberry Pi requirements :** 

<b>Config.txt :</b>  
In the event of an unexpected restart, this will allow not to open a solenoid valve by mistake.  
I need to add the following to the config.txt file to force gpio output and high state on gpio during the boot sequence :    

> gpio=4-13=op,dh  
> gpio=16-27=op,dh 

Gpio 2,3 are used for I2C (rtc and lcd)  
Gpio 14-15 are reserved and cannot be used !   

=> 22 gpio are therefore usable  

<b>Cron :</b>
 - start the main.py at startup
 - start the mqtt_subscribe.py at startup
 - in contrab -e:
   > @reboot sleep 20; sh /home/pi/launcher_arrosage.sh

<b>Raspi-config :</b>  
 - i2c must be activated (rtc + lcd)
 - spi must be deactivated  

**Functional Diagram :**

![Functional_Diagram](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/irripi.png)

**Electric Parts**

 - 1x Circuit breaker 2A 230v
 - 1x Electrical outlet 230v
 - 1x AC 24v 1,6A output rail din power supply (for solenoid valves) [links](https://www.amazon.fr/gp/product/B00F4QIL06/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1)
 - 1x DC 5v 2.5A output power supply (for raspberry, esp8266, relay, electronic)

**Electronics Parts**

- Raspberry Pi 2b + micro sd 
- 22x relay 5v
- 22x button 3 positions
- 1x button 2 positions
- 23x Screw Fuse Terminal Block rail din [links](https://fr.aliexpress.com/item/32957557760.html?spm=a2g0o.order_list.0.0.21ef5e5bLPmCsD&gatewayAdapt=glo2fra)
- 22x fuse 20x5 0.5A
- 1x fuse 20x5 2A 
- 1x lcd 20x4 i2c 5v
- 1x rtc module DS3231 i2c 5v

![Electronics_Box](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/electronics_box.jpg)
![Electronics_Box](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/electronics_box2.jpg)


**Web App :**

The web app  :  

![web app irripi](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/webapp1.png)

**Schematic :**

![fritzing irripi rpi](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/irripi_bb.png)

**Side projects (in progress) :**
- Tank filling with esphome and home-assistant [link](https://github.com/NicoDupont/esp_remplissage_cuve)
- [in progress] tank monitoring with esphome and home-assistant [link](https://github.com/NicoDupont/Monitoring_Cuve_Arrosage)
- Irrigation circuit monitoring with esphome and home-assistant [link](https://github.com/NicoDupont/Monitoring_Arrosage)

**Incomplete Work :**
- mqtt
- web ui
- logging
- lcd
- code

**Futur improvements :**
 - Improve WebUI
 - Multiple sequence
 - Add condition with rain meter
 - Improve code / mqtt
 - Clean the box with good cable management

**Integration in [Home-Assistant](https://www.home-assistant.io/)** **

![Home-Assistant lovelace](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/lovelace.png)


