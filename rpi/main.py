"""
* -----------------------------------------------------------------------------------
* Last update :   13/06/2024
* Arrosage Automatique / IrriPi
* Main launch script
* -----------------------------------------------------------------------------------
"""
#conda install -c conda-forge mysql-connector-python
# if numpy error on raspberrypi :
#sudo apt-get install python-dev libatlas-base-dev 
import datetime,time
from watering import Watering
from sequence import ComputeSequence
from anomaly import AnomalyDetection,MqttStatusAnomaly
from function import GetJsonData,GetDayTime,UpdateSequence,LoadData,ConfigLogging,MqttStatusZoneSequence,IsProgrammed,PublishMqtt
import yaml
import RPi.GPIO as GPIO
import pandas as pd
import logging

if __name__ == '__main__':
    #---------------------------------------
    # parameters for the script from config.yaml
    CONFIG_FILE = 'config.yaml'
    with open(CONFIG_FILE) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    #---------------------------------------
    #initialise gpio => recupération depuis fichier de config ?
    #list_gpio = [4,17,27,22,10,9,11,5,6,13,19,26,21,20,16,12,7,8,25,24,23,18]
    list_gpio = config['p_gpio']
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    for gpio in list_gpio:
        GPIO.setup(gpio, GPIO.OUT)
        GPIO.output(gpio, GPIO.HIGH)

    ZONE_PARAMETER_FILE = config['p_zp_file']         # configuration of the solenoid valves (=zone) for watering
    GLOBAL_SETTINGS_FILE =  config['p_gp_file']      # global parameters for irrigation
    ZONE_SEQUENCE_FILE =  config['p_zone_file']       # calculated sequence for watering
    SEQUENCE_FILE =  config['p_sequence_file']       # calculated sequence for watering
    ACTIVE_ZONE_FILE = config['p_az_file']            # file of the active zone for lcd
    RPI_NUMBER =  config['p_rpi']                     # if I need more than one rpi to manage all solenoid valves
    IP_WEB_SERVER =  config['p_ip_web']               # ip of local web server                
    IP_MQTT_SERVER =  config['p_ip_mqtt']             # ip of local mqtt server    
    IP_HA_SERVER =  config['p_ip_ha']                  # ip of local ha instance   
    IP_WEB =  config['p_ip_www']                  # ip for test internet         
    DELAY_TIME_SEQUENCE = config['p_delay_sequence']  # time in minutes between two sequences
    MIN_TIME_SEQUENCE = config['p_min_runtime']       # minimum run time for watering
    MAX_TIME_SEQUENCE = config['p_max_runtime']       # maximum run time for watering
    SLEEP_TIME_LOOP = config['p_sleep_loop']          # time in seconds between two loops
    RUN_WATERING= config['p_watering']             # watering management yes or no
    DETECT_ANOMALY = config['p_anomaly']    # take care of any anomalies
    LOG_LEVEL_STREAM = config['p_log_level_stream']   # log level to be write like print  NOTSET | DEBUG | INFO | WARNING | ERROR | CRITICAL
    LOG_LEVEL_FILE = config['p_log_level_file']       # log level to be write in log file  NOTSET | DEBUG | INFO | WARNING | ERROR | CRITICAL

    #--------------------------------------
    #initialise logging config
    #jour = GetDayTime(0)
    logger = logging.getLogger(__name__)#.addHandler(logging.NullHandler())
    #logfile = "log/arrosage_"+str(jour.day)+"_"+str(jour.month)+"_" +str(jour.year)+".txt"
    logfile = "log/arrosage.txt"
    ConfigLogging(logger,logfile,LOG_LEVEL_STREAM,LOG_LEVEL_FILE,True)

    #https://stackoverflow.com/questions/5974273/python-avoid-passing-logger-reference-between-functions
    #---------------------------------------
    # NUMBER_LOOP
    i=0
    while 1==1: #loop launch
        i+=1
        actual_day = GetDayTime(0)
        #prev_day = GetDayTime(-1) 
        # ----------------------------------------------------
        # global settings 
        global_settings = LoadData('select * from Parameter limit 1',logger,file=GLOBAL_SETTINGS_FILE)
        global_coef = global_settings["coef"].iloc[0]
        mode = global_settings["mode"].iloc[0]
        sequence_demande = global_settings["sequence_demande"].iloc[0]
        heure_demande = global_settings["heure_demande"].iloc[0]
        minute_demande = global_settings["minute_demande"].iloc[0]
        logger.debug(f'mode arrosage: {mode}')
        # ----------------------------------------------------
        # sequences settings
        sequence_settings = LoadData('select * from Sequence where active=1',logger,file=SEQUENCE_FILE)
        # ----------------------------------------------------
        # zones settings
        zone_settings = LoadData("select a.id_sv,a.type,a.sv,a.order,a.gpio,a.name,a.open,(case when b.active=0 then 0 else a.active end) as active,a.sequence,a.duration,a.test,a.even,a.odd,a.monday,a.tuesday,a.wednesday,a.thursday,a.friday,a.saturday,a.sunday,a.coef,a.rpi from Zone as a left join Sequence as b on a.sequence=b.seq where a.type='zone'",logger,file=ZONE_PARAMETER_FILE)
        logger.debug("Zone:")
        logger.debug(zone_settings.head())
        # ----------------------------------------------------
        # calculate the solenoid valve launch sequence by sequence and order
        zone_active = zone_settings[zone_settings.active.eq(1)]
        logger.debug("Zone active:")
        logger.debug(zone_active.head())
        # ----------------------------------------------------
        # iterate over sequence to compute each sequence 
        if not sequence_settings.empty and not zone_active.empty:
            for index, row in sequence_settings.iterrows():
                sequence = row["seq"]
                hstart = row["heure"]
                mstart = row["minute"]

                if mode == 'Demande' and sequence_demande==sequence:
                    starting_date = datetime.datetime(actual_day.year, actual_day.month, actual_day.day,hour=int(heure_demande),minute=int(minute_demande))
                else:
                    starting_date = datetime.datetime(actual_day.year, actual_day.month, actual_day.day,hour=int(hstart),minute=int(mstart))

                #calculation of the sequence for the watering zones by sequence number
                zone_sequence = ComputeSequence(sequence,starting_date,zone_active,global_coef,DELAY_TIME_SEQUENCE,MIN_TIME_SEQUENCE,MAX_TIME_SEQUENCE,logger)
                logger.debug("Zone Sequence:")
                logger.debug(f"zone :{sequence}")
                logger.debug(zone_sequence.head())
                if isinstance(zone_sequence, pd.DataFrame):
                    zone_active = zone_active.merge(zone_sequence, how='left', on=['order','sequence'])
        
            #filter data if no sequence active and add boolean if sv is planned today.
            logger.debug(zone_active.head())
            zone_active['planned']=zone_active.apply(lambda row: IsProgrammed(row["sv"],row["StartingDate"],row["EndDate"],actual_day,row["even"],row["odd"],row["monday"],row["tuesday"],row["wednesday"],row["thursday"],row["friday"],row["saturday"],row["sunday"],True,logger), axis=1)
            zone_active= zone_active[zone_active['StartingDate'].notnull()]
            # update calculated sequences to the database
            UpdateSequence('SequenceZone',zone_active[['id_sv','sv','name','sequence','order','open','duration','StartingDate','EndDate','planned']],logger)

        else:
            logger.warning('Aucune sequence ou zone active')
            #list_columns=['id_sv', 'sv', 'order', 'gpio', 'name', 'open','active', 'sequence', 'duration', 'even', 'odd', 'monday', 'tuesday','wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'coef', 'rpi','StartingDate', 'EndDate']
            #zone_active = pd.DataFrame(columns=list_columns)
            #create an empty dataframe if no active zone or sequence
            zone_active = pd.DataFrame()       #empty dataframe
            # update calculated sequences to the database
            UpdateSequence('SequenceZone',pd.DataFrame(columns=['id_sv','sv','name','sequence','order','open','duration','StartingDate','EndDate','planned']),logger)

        # dataframe of gpio+sv which are not in the sequence to deactivate them if they were previously active
        zone_inactive = zone_settings[zone_settings.active.ne(1)][["gpio","sv","rpi","open"]]
        if zone_inactive.empty:
            logger.debug("Aucune zone inactive")
        # ----------------------------------------------------
        # recover pontential anomalies 
        if DETECT_ANOMALY:
            anomaly = AnomalyDetection(global_settings,IP_WEB_SERVER,IP_HA_SERVER,IP_MQTT_SERVER,IP_WEB,logger)
            MqttStatusAnomaly(anomaly,logger)
            if anomaly[0] and anomaly[1] == False:
                logger.warning("Anomaly detected => Liste des anomalies :")
                logger.warning(anomaly[2])
            if anomaly[1]:
                logger.error("Critical Anomaly detected => Liste des anomalies :")
                logger.error(anomaly[2])
            if anomaly[0]==False and anomaly[1] == False:
                logger.debug("Aucune Anomalie")
        
        # ----------------------------------------------------
        # opening or closing control of the solenoid valves for watering
        if RUN_WATERING: 
            Watering(i,anomaly[1],zone_inactive,zone_active,global_settings,RPI_NUMBER,actual_day,logger)  
            MqttStatusZoneSequence(logger) #push mqtt info about zone and sequence to the brocker

        # ----------------------------------------------------
        #wait SLEEP_TIME_LOOP seconds for next loop
        time.sleep(SLEEP_TIME_LOOP)
        PublishMqtt(i,"status/loop_main",logger)
        logger.debug("==============     FIN LOOP            ==============")
        logger.debug("=====================================================")
    # ----------------------------------------------------
    #after while => end of the script if we going out off the loop
    GPIO.cleanup()
    logger.error("END LOOP")
