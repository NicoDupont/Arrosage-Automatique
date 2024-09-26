# Arrosage Automatique

A diy project to automate my irrigation system.  

Last Update : 16/07/2024  
This is the second working version for summer 2024, it will be adapted for 2025 or late 2024.

- python scripts improved
- webapp improved
- mqtt improved
- overall improvement of functionality

**Main Goal : replace one or more irrigation controllers and do it by mylself.**    

 **Big Concept :**

- Logic is done by python scripts on a raspberry pie

- Data management is done with an sql data base, mqtt is used to monitor and control the systeme from HA

- UI is based on a web application (home assistant can be used too(with mqtt))

- Sensors data comes from home-assistant/esphome
  
  **Overall functional descriptions :**

- A WebApp allows me to manage each solenoid valve/zone, global parameters, see the latest events, the watering sequence and some data.
- A collection of python scripts are used to open or close the solenoid valves and compute the watering sequence(s). 
  - There is a winter/stop, test, sequence on demande, automatic and manual mode
  - The program checks some data to know if it can run watering
  - Status and events are recorded in the database, sent to an mqtt broker and displayed on an LCD screen
  - several zones and/or sequences can run simultaneously (depends on the power supply for the solenoid valve and the watering pump)
- config.yaml file is used to configure the script in addition with the database.
- I can bypass the programmation to directly power supply and open any solenoid valve I want with 3 positions switch wired for each solenoid valve.
- Mqtt autodiscovery for homeassistant can be used (first test for diagnostics and not finish actualy)
- There are a few built-in automations : max number of active solenoid valve, rainfall, calculate the coef duration in correlation with the outside temperature

**Side projects (in progress) :**

- Tank filling  [link](https://github.com/NicoDupont/esp_remplissage_cuve)
- [in progress] PCB for relays, lcd, rtc module [link](https://github.com/NicoDupont/PCB/tree/main/arrosage)
- [in progress] Irrigation circuit monitoring  [link](https://github.com/NicoDupont/Monitoring_Arrosage)
- [in progress] Tank monitoring  [link](https://github.com/NicoDupont/Monitoring_Cuve_Arrosage)

**Futur improvements :**

- Mqtt : redo/complete mqtt parts with complete autodiscovery in HA (no need to add entities in configuration.yaml, add cmd/state topic)
- Improve web ui (design, kpi, tank management, mqtt management)
- Possibility to put a zone in more than 1 sequence
- Clean and redo the watering box (electricity+electronics)

**Current limitations :**

- A sequence/zone cannot be straddled between 2 days due to the very simple operation of the programming
- All parameters cannot be updated from home assistant
- Events are visible only from the web interface
- web app is not complete

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
in contrab -e:

> @reboot sleep 20; sh /home/pi/launcher_arrosage.sh

<b>Raspi-config :</b>  

- i2c must be activated (rtc + lcd)
- spi must be deactivated  

<b>Mqtt autodiscovery in home assistant :</b>    

> run : python3 /home/pi/arrosage/mqtt_autodiscovery.py     

**Functional Diagram :**

![Functional_Diagram](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/irripi.png)

**Watering parts**

- I use rainbird dv100 24vac solenoid valve

**Electric Parts**

- 1x Circuit breaker 2A 230v
- 1x Electrical outlet 230v
- 1x AC 24v 1,6A output rail din power supply (for solenoid valves) [links](https://www.amazon.fr/gp/product/B00F4QIL06/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1)
- 1x DC 5v 2.5A output power supply (for raspberry, esp8266, relay, electronic...)

![Electronics_Box](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/electric_box.jpg)

**Electronics Parts**

- Raspberry Pi 2b + micro sd 
- 22x relay 5v
- 22x button 3 positions
- 1x button 2 positions
- 23x Screw Fuse Terminal Block rail din [links](https://fr.aliexpress.com/item/32957557760.html?spm=a2g0o.order_list.0.0.21ef5e5bLPmCsD&gatewayAdapt=glo2fra)
- 22x fuse 20x5 0.5A
- 1x fuse 20x5 2A
- 1x lcd 20x4 i2c 5v
- 1x rtc module DS3231 i2c 3.3v

![Electronics_Box](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/electronics_box.jpg)
![Electronics_Box](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/electronics_box2.jpg)

**Web App :**

The web app  :  

![web app irripi](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/webapp1.png)
![web app irripi](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/webapp2.png)
![web app irripi](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/webapp3.png)
![web app irripi](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/webapp4.png)

**Schematic :**

![fritzing irripi rpi](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/irripi_bb.png)

**Integration in [Home-Assistant](https://www.home-assistant.io/)**

![Home-Assistant lovelace](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/lovelace.png)
![Home-Assistant lovelace](https://github.com/NicoDupont/Arrosage-Automatique/blob/main/doc/mqtt.png)
