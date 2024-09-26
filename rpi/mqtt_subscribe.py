"""
* -----------------------------------------------------------------------------------
* Last update :  10/06/2024
* Arrosage Automatique
* Tache de récupération des données depuis mqtt pour maj la bdd (topics update from mosquito brocker)
* lister les topics + boucle sur txt / yaml / json ?
* -----------------------------------------------------------------------------------
"""

import paho.mqtt.client as mqtt
import yaml
import json
from sqlalchemy import create_engine 
import logging
from function import ConfigLogging,GetDayTime,RestartRpi,UpdateData,LogDatabase,LaunchTestRelais

if __name__ == '__main__':
	#---------------------------------------
	# parametres
	CONFIG_FILE = 'config.yaml'

	with open(CONFIG_FILE) as f:
		config = yaml.load(f, Loader=yaml.FullLoader)
	
	IP_BDD_SERVER = config['p_ip_bdd']
	USER_BDD = config['p_user_bdd']
	PASSWORD_BDD = config['p_password_bdd']
	NAME_DATABASE = config['p_database']
	IP_MQTT_BROKER = config['p_ip_mqtt']
	USER_MQTT = config['p_user_mqtt']
	PASSWORD_MQTT = config['p_password_mqtt']
	PORT_MQTT = config['p_port_mqtt']
	LOG_LEVEL_STREAM = config['p_log_level_stream']   # log level to be write like print  NOTSET | DEBUG | INFO | WARNING | ERROR | CRITICAL
	LOG_LEVEL_FILE = config['p_log_level_file']       # log level to be write in log file  NOTSET | DEBUG | INFO | WARNING | ERROR | CRITICAL
	FILE_TOPIC_MQTT = config['p_topics_mqtt']
	PREFIX_MQTT= config['P_prefix_mqtt']    
	DEVICE_MQTT= config['p_device_mqtt']    
	#--------------------------------------
	#initialise logging config
	actual_day = GetDayTime(0)
	logger = logging.getLogger(__name__)#.addHandler(logging.NullHandler())
	#logfile = "log/mqtt_subscribe"+str(actual_day.day)+"_"+str(actual_day.month)+"_" +str(actual_day.year)+".txt"
	logfile = "log/mqtt_subscribe.txt"
	ConfigLogging(logger,logfile,LOG_LEVEL_STREAM,LOG_LEVEL_FILE,True)

	#mqtt_logger = logging.getLogger("MqttCon")

	f = open(FILE_TOPIC_MQTT)
	topics = json.load(f)
	f.close()

	list_topics = []
	for subpart in topics:
		for type_topic, listtopic in subpart.items():
			for value in listtopic:
				logger.debug("partie {0} topics : {1} bdd : {2} table : {3}".format(type_topic,value['topic'],value['field'],value['table']))
				list_topics.append(tuple([type_topic,PREFIX_MQTT+"/"+DEVICE_MQTT+"/"+value['topic'],value['field'],value['table']]))
	logger.debug("Topic settings :")

	subscribe_topics = []
	for type_topic,topic_name,field_name,table_name in list_topics:
		topic = topic_name
		subscribe_topics.append(topic)
	logger.debug("Topics to subscribe :")
	logger.debug(subscribe_topics)
	for topic in subscribe_topics:
		logger.debug(topic)

	# Fonction appelée lorsque le client reçoit un message d'un sujet auquel il est abonné
	# prevoir un publish sur topic state pour 2025 apres reception du susbscribe 
	def on_message(client, userdata, message):
		msg_payload = str(message.payload.decode("utf-8")).strip()
		msg_topic = message.topic
		if msg_topic[:19] != 'ha/arrosage/status/' and msg_topic[:13] != 'ha/arrosage/Z' and msg_topic[:13] != 'ha/arrosage/S':
			logger.info(f'topic : {msg_topic} value :{msg_payload}')
		#print("Message reçu sur le sujet '" + message.topic + "': ", str(message.payload.decode("utf-8")))
		if msg_topic=="ha/arrosage/status/restart" and msg_payload=='restart':
			logger.info("restart")
			LogDatabase(msg_topic.replace('ha/arrosage/',''),msg_payload,'','','mqtt',logger)
			RestartRpi(logger)
		else:
			if msg_topic=="ha/arrosage/status/test_relais" and msg_payload=='test_relais':
				logger.info("test_relais")
				LogDatabase(msg_topic.replace('ha/arrosage/',''),msg_payload,'','','mqtt',logger)
				LaunchTestRelais(logger)
			else:
				if msg_payload != '':
					for type_topic,topic_name,field_name,table_name in list_topics:
						if msg_topic==topic_name and type_topic[:1] in ['Z','S']:
							field_filter = "sv" if type_topic[:1]=='Z' else "Seq"
							LogDatabase(msg_topic.replace('ha/arrosage/',''),msg_payload,table_name,field_name,'mqtt',logger)
							UpdateData(table_name,field_name,msg_payload,field_filter,type_topic,type_topic[:1],logger)
							logger.info(f'update topic : {topic_name} value : {msg_payload}')
						else:
							if msg_topic==topic_name and type_topic == 'param':
								LogDatabase(msg_topic.replace('ha/arrosage/',''),msg_payload,table_name,field_name,'mqtt',logger)
								UpdateData(table_name,field_name,msg_payload,'','',type_topic[:1],logger)
								logger.info(f'update topic : {topic_name} value : {msg_payload}')
				else:
					logger.warning(f'Payload vide topic : {msg_topic}')


	def on_disconnect(client, userdata, rc):
		logger.warning(f"Disconnected from MQTT broker ! return code rc : {rc}")
		# Tenter de se reconnecter
		while rc != 0:
			logger.warning(f"Attempt to reconnect in 2 minutes ! code rc : {rc}")
			time.sleep(120)
			try:
				client.reconnect()
			except:
				logger.warning(f"Reconnection problem ! code rc : {rc}")
				pass

	def on_log(client, userdata, level, buf):
		logger.info(f"SYSTEM: {buf}")

	def on_connect(client, userdata, flags, rc, properties=None):
		if rc==0:
			logger.info("Connected to MQTT Broker")
		else:
			logger.error(f"Connection failed to MQTT Broker RC : {rc}")

	client = mqtt.Client(protocol = mqtt.MQTTv5)
	client.username_pw_set(USER_MQTT, PASSWORD_MQTT)
	client.connect(IP_MQTT_BROKER, PORT_MQTT)
	#client.subscribe(subscribe_topics)
	client.subscribe("ha/arrosage/#")
	client.on_connect = on_connect
	client.on_message = on_message
	client.on_log = on_log
	client.on_disconnect = on_disconnect
	client.loop_forever(retry_first_connection=True)
	#client.reconnect_delay_set(60,60)
	#client.reconnect