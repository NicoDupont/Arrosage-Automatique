import paho.mqtt.client as mqtt
import random

IP_MQTT_BROKER = '192.168.1.18'
USER_MQTT = 'nicolas'
PASSWORD_MQTT = ''
PORT_MQTT = 1883
DEBUG = True
state_topic1 = 'ha/arrosage/pression_canal'
state_topic2 = 'ha/arrosage/pression_cuve'


data1 = random.randint(0, 10)
data2 = random.randint(0, 10)

print(data1)
print(data2)

def PublishMqtt(payload,topic,debug):
    try:
        client = mqtt.Client("arrosage") #create new instance
        client.username_pw_set(username=USER_MQTT,password=PASSWORD_MQTT) #set user and password
        client.connect(host=IP_MQTT_BROKER,port=PORT_MQTT) #connect to broker
        client.publish(topic,str(payload)) #publish data to the specified topic
        client.disconnect() #disconnect
        if debug:
            print('Mqtt => Topic : {0} => Payload : {1}'.format(topic,payload))
    except:
        if debug:
            print('Probleme with Mqtt to publish data')

PublishMqtt(data1,state_topic1,DEBUG)
PublishMqtt(data2,state_topic2,DEBUG)