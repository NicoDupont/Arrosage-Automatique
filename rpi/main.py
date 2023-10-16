"""
* -----------------------------------------------------------------------------------
* Last update :   12/09/2023
* Project Irripi
* Main Python script to manage watering
* -----------------------------------------------------------------------------------
"""
#conda install -c conda-forge mysql-connector-python
# if numpy error on raspberrypi :
#sudo apt-get install python-dev libatlas-base-dev 
import datetime,time
from watering import Watering
from sequence import ComputeSequence
from anomaly import AnomalyDetection
from function import GetJsonData,GetDayTime,WriteJsonData,Print2Lcd,DisplayActiveZone,UpdateParameter,UpdateBdd
import lcddriver  #comment if not lcd
import yaml
import RPi.GPIO as GPIO
import pandas as pd

#---------------------------------------
#---------------------------------------
# parameters for the script from config.yaml
CONFIG_FILE = 'config.yaml'

with open(CONFIG_FILE) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    #print(config)
 
ACTIVE_DEBUG = config['p_debug']                  # print debug data
ZONE_PARAMETER_FILE = config['p_zp_file']         # configuration of the solenoid valves (=zone) for watering
GLOBAL_PARAMETER_FILE =  config['p_gp_file']      # global parameters for irrigation
ZONE_SEQUENCE_FILE =  config['p_zone_file']       # calculated sequence for watering
ACTIVE_ZONE_FILE = config['p_az_file']            # file of the active zone for lcd
RPI_NUMBER =  config['p_rpi']                     # if I need more than one rpi to manage all solenoid valves
IP_WEB_SERVER =  config['p_ip_web']               # ip web server                
IP_MQTT_SERVER =  config['p_ip_mqtt']             # ip mqtt server              
DELAY_TIME_SEQUENCE = config['p_delay_sequence']  # time in minutes between two sequences
MIN_TIME_SEQUENCE = config['p_min_runtime']       # minimum run time for watering
MAX_TIME_SEQUENCE = config['p_max_runtime']       # maximum run time for watering
SWITCHOVER_TIME = config['p_switchover_time']     # switchover time for calculating the watering sequence
SLEEP_TIME_LOOP = config['p_sleep_loop']          # time in seconds between two loops
NUMBER_LOOP = config['p_nb_loop']                 # number of loop 
ACTIVE_WATERING= config['p_watering']             # watering management yes or no
ACTIVE_LCD = config['p_lcd_screen']               # use or not the lcd
PROJECT_NAME = config['p_name']                   # name of the project
PROJECT_VERSION = config['p_version']             # version number of the project
PROJECT_DATE_VERSION = config['p_date_version']   # date version of the project
ACTIVE_ANOMALY_DETECTION = config['p_anomaly']    # take care of any anomalies
WAIT_TIME_LCD = config['p_lcd_sleep_time']        # time in seconds to keep display
ACTIVE_EVENTS_LOG = config['p_log_bdd']           # log events or not on the database
UPDATE_STATUS = config['p_status']                # update UPDATE_STATUS on database
UPDATE_MESURE = config['p_mesure']                # update mesure or not
UPDATE_DATA = config['p_update_data']             # update json files or not
PUBLISH_MQTT = config['p_mqtt']   

#---------------------------------------
#---------------------------------------
#initialise the lcd screen
if ACTIVE_LCD:
    lcd = lcddriver.lcd()
    Print2Lcd(lcd,WAIT_TIME_LCD,True,"{0} {1} {2}".format(PROJECT_NAME,PROJECT_VERSION,PROJECT_DATE_VERSION),"Demarrage...","","") 
    Print2Lcd(lcd,WAIT_TIME_LCD,False,"","Initialisation..."," "," ") 

#---------------------------------------
#---------------------------------------
#initialise gpio
#list_gpio_zone =  GetJsonData(ZONE_PARAMETER_FILE,ACTIVE_DEBUG)['gpio'].tolist()
#list_gpio = list_gpio_zone
list_gpio = [4,17,27,22,10,9,11,5,6,13,19,26,21,20,16,12,7,8,25,24,23,18]
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
for gpio in list_gpio:
    GPIO.setup(gpio, GPIO.OUT)
    GPIO.output(gpio, GPIO.HIGH)

#---------------------------------------
#---------------------------------------
# NUMBER_LOOP
i=0
list_columns=['id_sv', 'sv', 'order', 'gpio', 'name', 'open','active', 'sequence', 'duration', 'even', 'odd', 'monday', 'tuesday','wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'coef', 'rpi','StartingDate', 'EndDate']

while 1==1: #loop launch

    i+=1
    if ACTIVE_LCD:
        lcd = lcddriver.lcd()
    else:
        lcd = ''

    day = GetDayTime(0,ACTIVE_DEBUG)
    prev_day = GetDayTime(-1,ACTIVE_DEBUG)    
    if ACTIVE_LCD:
        Print2Lcd(lcd,WAIT_TIME_LCD,True,"{0} {1} {2}".format(PROJECT_NAME,PROJECT_VERSION,PROJECT_DATE_VERSION),"Recuperation :","Date Et Heure","{0}-{1}-{2} {3}:{4}".format(day.day,day.month,day.year,day.hour,day.minute))        

    # ----------------------------------------------------
    # update data from the database
    if ACTIVE_LCD:
        Print2Lcd(lcd,WAIT_TIME_LCD,False,"","Mise a jour :","Parametres"," ")  

    if UPDATE_DATA:
        #update parameters
        UpdateParameter('select sv,open from Zone where open=1',ACTIVE_ZONE_FILE,False,'',ACTIVE_DEBUG)
        UpdateParameter("select * from Zone where type='zone'",ZONE_PARAMETER_FILE,False,'',ACTIVE_DEBUG)
        UpdateParameter('select * from Parameter limit 1',GLOBAL_PARAMETER_FILE,False,'',ACTIVE_DEBUG)

    # ----------------------------------------------------
    # global parameters for watering from the bdd     
    global_param = GetJsonData(GLOBAL_PARAMETER_FILE,ACTIVE_DEBUG)
    for index, row in global_param.iterrows():
        gcoef = row["duree_coef"]
        hstart = row["heure_debut_sequence"]
        mstart = row["minute_debut_sequence"]
        hstartDemande = row["heure_debut_sequence_demande"]
        mstartDemande = row["minute_debut_sequence_demande"]
        mode = row["mode"]

    # ----------------------------------------------------
    # calculate the solenoid valve launch sequence for watering
    # calculate the start date and time for the schedule
    if mode == 'Demande':
        starting_date_hour = datetime.datetime(day.year, day.month, day.day,hour=int(hstartDemande),minute=int(mstartDemande))
    else:
        if hstart>=SWITCHOVER_TIME and day.hour >=0 and day.hour<=SWITCHOVER_TIME-1:
            starting_date_hour = datetime.datetime(prev_day.year, prev_day.month, prev_day.day,hour=int(hstart),minute=int(mstart))
        else:
            starting_date_hour = datetime.datetime(day.year, day.month, day.day,hour=int(hstart),minute=int(mstart))

    # solenoid valve parameters
    zone_param = GetJsonData(ZONE_PARAMETER_FILE,ACTIVE_DEBUG)
    #calculation of the sequence for the watering zones
    zone_sequence = ComputeSequence(1,starting_date_hour,zone_param,gcoef,DELAY_TIME_SEQUENCE,MIN_TIME_SEQUENCE,MAX_TIME_SEQUENCE,ACTIVE_DEBUG)
    if isinstance(zone_sequence, pd.DataFrame):
        zone_active = zone_param[zone_param.active.eq(1)]
        zone_active = zone_active.merge(zone_sequence, how='inner', on='order')
    else:
        #initialise empty dataframe
        zone_active = pd.DataFrame(columns=list_columns)
    
    WriteJsonData(zone_active[['id_sv','sv','name','order','open','duration','StartingDate','EndDate']],ZONE_SEQUENCE_FILE,ACTIVE_DEBUG)
    if ACTIVE_DEBUG:
        print("-------------- ACTIVE ZONE --------------")
        print(zone_active)
        print("Number of active zone : ",zone_active.shape[0])

    # dataframe of gpio+sv which are not in the sequence to deactivate them if they were previously active
    zone_n_active = zone_param[zone_param.active.ne(1)][["gpio","sv","rpi","open"]]
    
    if ACTIVE_DEBUG:
        print("------------ NON ACTIVE ZONE ------------")
        print(zone_n_active)
        print("Number of non active zone : ",zone_n_active.shape[0])

    # ----------------------------------------------------
    # update sequences data to the database
    if UPDATE_DATA:
        #update sequence
        UpdateBdd('SequenceZone',ZONE_SEQUENCE_FILE,True,ACTIVE_DEBUG)

    # ----------------------------------------------------
    # recover pontential anomalies
    if ACTIVE_LCD:
        Print2Lcd(lcd,WAIT_TIME_LCD,False,"","Detection :","Anomalie(s)..."," ")       
    if ACTIVE_ANOMALY_DETECTION:
        anomaly = AnomalyDetection(zone_n_active,zone_active,global_param,IP_WEB_SERVER,IP_MQTT_SERVER,RPI_NUMBER,day,lcd,ACTIVE_LCD,WAIT_TIME_LCD,ACTIVE_EVENTS_LOG,PUBLISH_MQTT,ACTIVE_DEBUG)
        if ACTIVE_DEBUG:
            if anomaly:
                print("Anomaly detected")
    else:
        anomaly = False

    # ----------------------------------------------------
    # opening or closing control of the solenoid valves for watering
    if ACTIVE_WATERING and anomaly == False:
        if ACTIVE_LCD:
            Print2Lcd(lcd,WAIT_TIME_LCD,False,"","Lancement :","Arrosage Zone"," ")  
        if ACTIVE_DEBUG:  
            print("-------------------------------")          
            print('Partie Arrosage:')
        Watering(i,zone_n_active,zone_active,global_param,RPI_NUMBER,day,ACTIVE_DEBUG,ACTIVE_EVENTS_LOG,lcd,ACTIVE_LCD,WAIT_TIME_LCD,PROJECT_NAME,PROJECT_VERSION,PROJECT_DATE_VERSION)
    else:
        if ACTIVE_DEBUG:
            print("-------------------------------") 
            print('Arrosage non activé ou anomalie présente')
        if ACTIVE_LCD:
            Print2Lcd(lcd,WAIT_TIME_LCD,False,"","Arrosage Zone :","Desactivee"," ")

    # ----------------------------------------------------
    # display on the lcd the active zone or none
    if ACTIVE_LCD:
        DisplayActiveZone(ACTIVE_ZONE_FILE,lcd,WAIT_TIME_LCD,ACTIVE_DEBUG)
    
    # ----------------------------------------------------
    #wait SLEEP_TIME_LOOP seconds for next loop
    time.sleep(SLEEP_TIME_LOOP)

# ----------------------------------------------------
#after while => end of the script if we going out off the loop
GPIO.cleanup()
print('END LOOP')
if ACTIVE_LCD:
    Print2Lcd(lcd,WAIT_TIME_LCD,False,"","Fin du script :","Relancer main.py","Ou redemarrer")
