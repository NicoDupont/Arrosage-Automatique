"""
* -----------------------------------------------------------------------------------
* Last update :  06/09/2023
* Project Irripi
* Tache de récupération des données depuis mqtt pour maj la bdd
* Le programme doit tourner en fond
* -----------------------------------------------------------------------------------
"""

import paho.mqtt.client as mqtt
import yaml
from sqlalchemy import create_engine 

#---------------------------------------
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
DEBUG = config['p_debug']    
DEBUG = False   

topic_field_param = {"ha/arrosage/parametre/mode":"mode", 
                   "ha/arrosage/parametre/source_arrosage":"source",
                   "ha/arrosage/parametre/heure_debut_sequence":"heure_debut_sequence",
                   "ha/arrosage/parametre/heure_debut_sequence_demande":"heure_debut_sequence_demande",
                   "ha/arrosage/parametre/duree_test":"duree_test",
                   "ha/arrosage/parametre/duree_coef":"duree_coef",
                   "ha/arrosage/parametre/pression_seuil_haut":"pression_seuil_haut",
                   "ha/arrosage/parametre/pression_seuil_bas":"pression_seuil_bas",
                   "ha/arrosage/parametre/delta_pression_filtre_max":"delta_pression_filtre_max",
                   "ha/arrosage/parametre/gestion_cuve":"gestion_cuve",
                   "ha/arrosage/parametre/test_pression_canal":"test_pression_canal",
                   "ha/arrosage/parametre/test_pression_cuve":"test_pression_cuve",
                   "ha/arrosage/parametre/test_pression_ville":"test_pression_ville",
                   "ha/arrosage/parametre/nb_cuve_ibc":"nb_cuve_ibc",
                   "ha/arrosage/parametre/nb_litre_cuve_ibc":"nb_litre_cuve_ibc",
                   "ha/arrosage/parametre/seuil_min_capacite_cuve":"seuil_min_capacite_cuve",
                   "ha/arrosage/parametre/seuil_max_capacite_cuve":"seuil_max_capacite_cuve",
                   "ha/arrosage/parametre/test_hauteur_eau_cuve":"test_hauteur_eau_cuve",
                   "ha/arrosage/parametre/seuil_capacite_remplissage_auto_cuve":"seuil_capacite_remplissage_auto_cuve",
                   "ha/arrosage/parametre/minute_debut_sequence": "minute_debut_sequence",
                   "ha/arrosage/parametre/minute_debut_sequence_demande": "minute_debut_sequence_demande"
                   }

topic_etat_zone = {"ha/arrosage/Z1/etat":"Z1", 
                   "ha/arrosage/Z2/etat":"Z2",
                   "ha/arrosage/Z3/etat":"Z3", 
                   "ha/arrosage/Z4/etat":"Z4",
                   "ha/arrosage/Z5/etat":"Z5", 
                   "ha/arrosage/Z6/etat":"Z6",
                   "ha/arrosage/Z7/etat":"Z7", 
                   "ha/arrosage/Z8/etat":"Z8",
                   "ha/arrosage/Z9/etat":"Z9", 
                   "ha/arrosage/Z10/etat":"Z10",
                   "ha/arrosage/Z11/etat":"Z11", 
                   "ha/arrosage/Z12/etat":"Z12",
                   "ha/arrosage/Z13/etat":"Z13", 
                   "ha/arrosage/Z14/etat":"Z14",
                   "ha/arrosage/Z15/etat":"Z15", 
                   "ha/arrosage/Z16/etat":"Z16",
                   "ha/arrosage/Z17/etat":"Z17", 
                   "ha/arrosage/Z18/etat":"Z18",
                   "ha/arrosage/Z19/etat":"Z19", 
                   "ha/arrosage/Z20/etat":"Z20",
                   "ha/arrosage/Z21/etat":"Z21", 
                   "ha/arrosage/Z22/etat":"Z22"
                   }

topic_active_zone = {"ha/arrosage/Z1/active":"Z1", 
                   "ha/arrosage/Z2/active":"Z2",
                   "ha/arrosage/Z3/active":"Z3", 
                   "ha/arrosage/Z4/active":"Z4",
                   "ha/arrosage/Z5/active":"Z5", 
                   "ha/arrosage/Z6/active":"Z6",
                   "ha/arrosage/Z7/active":"Z7", 
                   "ha/arrosage/Z8/active":"Z8",
                   "ha/arrosage/Z9/active":"Z9", 
                   "ha/arrosage/Z10/active":"Z10",
                   "ha/arrosage/Z11/active":"Z11", 
                   "ha/arrosage/Z12/active":"Z12",
                   "ha/arrosage/Z13/active":"Z13", 
                   "ha/arrosage/Z14/active":"Z14",
                   "ha/arrosage/Z15/active":"Z15", 
                   "ha/arrosage/Z16/active":"Z16",
                   "ha/arrosage/Z17/active":"Z17", 
                   "ha/arrosage/Z18/active":"Z18",
                   "ha/arrosage/Z19/active":"Z19", 
                   "ha/arrosage/Z20/active":"Z20",
                   "ha/arrosage/Z21/active":"Z21", 
                   "ha/arrosage/Z22/active":"Z22"
                   }

topic_duree_zone = {"ha/arrosage/Z1/duree":"Z1", 
                   "ha/arrosage/Z2/duree":"Z2",
                   "ha/arrosage/Z3/duree":"Z3", 
                   "ha/arrosage/Z4/duree":"Z4",
                   "ha/arrosage/Z5/duree":"Z5", 
                   "ha/arrosage/Z6/duree":"Z6",
                   "ha/arrosage/Z7/duree":"Z7", 
                   "ha/arrosage/Z8/duree":"Z8",
                   "ha/arrosage/Z9/duree":"Z9", 
                   "ha/arrosage/Z10/duree":"Z10",
                   "ha/arrosage/Z11/duree":"Z11", 
                   "ha/arrosage/Z12/duree":"Z12",
                   "ha/arrosage/Z13/duree":"Z13", 
                   "ha/arrosage/Z14/duree":"Z14",
                   "ha/arrosage/Z15/duree":"Z15", 
                   "ha/arrosage/Z16/duree":"Z16",
                   "ha/arrosage/Z17/duree":"Z17", 
                   "ha/arrosage/Z18/duree":"Z18",
                   "ha/arrosage/Z19/duree":"Z19", 
                   "ha/arrosage/Z20/duree":"Z20",
                   "ha/arrosage/Z21/duree":"Z21", 
                   "ha/arrosage/Z22/duree":"Z22"
                   }

topics = []
for topic_name,field_name in topic_field_param.items():
    topic = (topic_name,1)
    topics.append(topic)

for topic_name,field_name in topic_etat_zone.items():
    topic = (topic_name,1)
    topics.append(topic)

for topic_name,field_name in topic_active_zone.items():
    topic = (topic_name,1)
    topics.append(topic)

for topic_name,field_name in topic_duree_zone.items():
    topic = (topic_name,1)
    topics.append(topic)

# Fonction maj données dans la bdd
def UpdateParamBdd(field,value,debug):
    try:
        db = create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(USER_BDD,PASSWORD_BDD,IP_BDD_SERVER,NAME_DATABASE), pool_recycle=3600)
        bdd = db.connect()
        sql = "update Parameter set {0}='{1}'".format(field,value)
        bdd.execute(sql)
        bdd.close()
        if debug:
            print("update Parameter set {0}='{1}'".format(field,value))
        return True
    except:
        if debug:
            print('Update KO for field : {0} valeur : {1} : MariaDb Problem @ {2}'.format(field,value,IP_BDD_SERVER))
        return False

# Fonction maj données etat zone
def UpdateZoneBdd(field,zone,value,debug):
    try:
        db = create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(USER_BDD,PASSWORD_BDD,IP_BDD_SERVER,NAME_DATABASE), pool_recycle=3600)
        bdd = db.connect()
        sql = "update Zone set {0}='{2}' where sv='{1}'".format(field,zone,value)
        bdd.execute(sql)
        bdd.close()
        if debug:
            print("update Zone set {0}='{2}' where sv='{1}'".format(field,zone,value))
        return True
    except:
        if debug:
            print('Update KO : MariaDb Problem @ '+IP_BDD_SERVER)
        return False

# Fonction appelée lorsque le client reçoit un message d'un sujet auquel il est abonné
def on_message(client, userdata, message):
    #print("Message reçu sur le sujet '" + message.topic + "': ", str(message.payload.decode("utf-8")))
    #parametre
    for topic_name,field_name in topic_field_param.items():
        if message.topic==topic_name:
            UpdateParamBdd(field_name,str(message.payload.decode("utf-8")),DEBUG)
    
    #etatzone
    for topic_name,zone in topic_etat_zone.items():
        if message.topic==topic_name:
            UpdateZoneBdd('open',zone,str(message.payload.decode("utf-8")),DEBUG)
    
    #activezone
    for topic_name,zone in topic_active_zone.items():
        if message.topic==topic_name:
            UpdateZoneBdd('active',zone,str(message.payload.decode("utf-8")),DEBUG)

    #dureezone
    for topic_name,zone in topic_duree_zone.items():
        if message.topic==topic_name:
            UpdateZoneBdd('duration',zone,str(message.payload.decode("utf-8")),DEBUG)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
        rc = client.reconnect()

# Création d'un client MQTT
client = mqtt.Client()
# Connexion au serveur MQTT
client.username_pw_set(USER_MQTT, PASSWORD_MQTT)
client.connect(IP_MQTT_BROKER, PORT_MQTT)
# Souscription à plusieurs sujets en utilisant un tuple pour spécifier les sujets et les niveaux de QoS
client.subscribe(topics)
# Indication de la fonction à appeler lors de la réception d'un message
client.on_message = on_message
#client.on_disconnect = on_disconnect
client.reconnect_delay_set(60,60)
# Boucle de traitement des messages
client.loop_forever()
