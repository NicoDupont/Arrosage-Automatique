"""
* -----------------------------------------------------------------------------------
* Last update :  07/05/2024
* Arrosage Automatique
* Script à executer pour créer le json pour l'autodiscovery
* IN PROGRESS NOT WORK
* -----------------------------------------------------------------------------------
"""

import paho.mqtt.client as mqtt
import json
import time
from function import LoadData,ConfigLogging,GetDayTime
import logging

IP_MQTT_BROKER = '192.168.1.125'
USER_MQTT = 'nicolas'
PASSWORD_MQTT = 'lkmjkgfdfrtpcv'
PORT_MQTT = 1883
MQTT_BDD_AUTODISCOVERY = "json/mqtt_bdd_autiscovery.json"
MQTT_AUTODISCOVERY = "json/mqtt_autiscovery_ha_test.json"
LOG_LEVEL_STREAM = 'DEBUG'   # log level to be write like print  NOTSET | DEBUG | INFO | WARNING | ERROR | CRITICAL
LOG_LEVEL_FILE = 'DEBUG'       # log level to be write in log file  NOTSET | DEBUG | INFO | WARNING | ERROR | CRITICAL
#--------------------------------------
#initialise logging config
jour = GetDayTime(0)
logger = logging.getLogger(__name__)#.addHandler(logging.NullHandler())
logfile = "log/mqtt_generate_json_autodiscovery"+str(jour.day)+"_"+str(jour.month)+"_" +str(jour.year)+".txt"
#logfile = "log/arrosage.txt"
ConfigLogging(logger,logfile,LOG_LEVEL_STREAM,LOG_LEVEL_FILE,False)

autodiscovery_config = LoadData("select * from mqtt where active=1;",MQTT_BDD_AUTODISCOVERY,logger)


payload = '{"entities": ['
for index, row in autodiscovery_config.iterrows():
    if payload != '{"entities": [':
        payload = payload+','
    payload = payload+'{"topic": "homeassistant/'+row["config_entitie"]+'/'+row["config_device"]+'/'+row["config_name"]+'/config,'
    payload = payload+'"payload": "{\"device\":{\"identifiers\":\"'
    payload = payload+row["device_identifiers"]+'\",\"manufacturer\":\"'+row["device_manufacturer"]+'\",\"model\":\"'+row["device_model"]+'\",\"name\":\"'+row["device_name"]+'\",\"configuration_url\":\"'+row["configuration_url"]+'\",\"sw_version\":\"'+row["sw_version"]+'\"},'
    payload = payload+'\"object_id\":\"'+row["object_id"]+'\",\"unique_id\":\"'+row["unique_id"]+'\",\"name\":\"'+row["name"]+'\",\"icon\":\"'+row["icon"]+'\",\"state_topic\":\"'+row["state_topic"]+'\",\"qos\":\"'+row["qos"]+',\"entity_category\":\"'+row["entity_category"]+'\"'
    if row["config_entitie"] == "switch":
        payload = payload+',\"command_topic\":\"'+row["command_topic"]+'\",\"payload_on\":\"'+row["payload_on"]+'\",\"payload_off\":\"'+row["payload_off"]+'\",\"state_on\":\"'+row["state_on"]+'\",\"state_off\":\"'+row["state_off"]+'\"'
    if row["config_entitie"] == "binary_sensor":
        payload = payload+',\"payload_on\":\"'+row["payload_on"]+'\",\"payload_off\":\"'+row["payload_off"]+'\"'
    if row["config_entitie"] == "number":
        payload = payload+'\"command_topic\":\"'+row["command_topic"]+'\",\"optimistic\":\"'+row["optimistic"]+'\",\"retain\":\"'+row["retain"]+'\",\"min\":\"'+row["min"]+'\",\"max\":\"'+row["max"]+'\",\"step\":\"'+row["step"]+'\",\"unit_of_measurement\":\"'+row["unit_of_measurement"]+'\"'
    if row["config_entitie"] == "select":
        payload = payload+',\"command_topic\":\"'+row["command_topic"]+'\",\"options\":'+row["options"]
    if row["config_entitie"] == "button":
        payload = payload+'\"command_topic\":\"'+row["command_topic"]+'\",\"retain\":\"'+row["retain"]+'\",\"payload_press\":\"'+row["payload_press"]+'\",\"entity_category\":\"'+row["entity_category"]+'\",\"device_class\":\"'+row["device_class"]+'\"'
    payload = payload+'}"'

payload = payload+']}'

f = open(MQTT_AUTODISCOVERY, "w")
f.write(payload)
f.close()

print("Fichier json autodiscovery mqtt créé")


