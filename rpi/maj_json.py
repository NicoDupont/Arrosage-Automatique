"""
* -----------------------------------------------------------------------------------
* Last update :   10/06/2024
* Arrosage Automatique / IrriPi
* Script to update json files to use them if the database is offline for any reason
* => utile ???
* -----------------------------------------------------------------------------------  
"""

from function import UpdateJson,ConfigLogging,GetDayTime,PublishMqtt
import yaml
import logging
import datetime,time
#import ntplib

if __name__ == '__main__':
    #---------------------------------------
    # parameters for the script from config.yaml
    CONFIG_FILE = 'config.yaml'

    with open(CONFIG_FILE) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    SEQUENCE_FILE =  config['p_sequence_file']       # calculated sequence for watering
    ZONE_SEQUENCE_FILE =  config['p_zone_file']       # calculated sequence for watering
    ZONE_PARAMETER_FILE = config['p_zp_file']         # configuration of the solenoid valves (=zone) for watering
    GLOBAL_PARAMETER_FILE = config['p_gp_file']      # global parameters for irrigation
    ACTIVE_ZONE_FILE = config['p_az_file']            # file of the active zone for lcd
    MQTT_BDD_AUTODISCOVERY_FILE = config['p_mqtt_bdd_autodiscovery_file']
    LOG_LEVEL_STREAM = config['p_log_level_stream']   # log level to be write like print  NOTSET | DEBUG | INFO | WARNING | ERROR | CRITICAL
    LOG_LEVEL_FILE = config['p_log_level_file']       # log level to be write in log file  NOTSET | DEBUG | INFO | WARNING | ERROR | CRITICAL
   
    #--------------------------------------
    #initialise logging config
    actual_day = GetDayTime(0)
    logger = logging.getLogger(__name__)#.addHandler(logging.NullHandler())
    #logfile = "log/maj_json_"+str(actual_day.day)+"_"+str(actual_day.month)+"_" +str(actual_day.year)+".txt"
    logfile = 'log/maj_json.txt'
    ConfigLogging(logger,logfile,LOG_LEVEL_STREAM,LOG_LEVEL_FILE,True)
    i=0
    while 1==1:
        i+=1
        UpdateJson('select sv,open,sequence from Zone where open=1',ACTIVE_ZONE_FILE,logger)
        UpdateJson("select a.id_sv,a.type,a.sv,a.order,a.gpio,a.name,a.open,(case when b.active=0 then 0 else a.active end) as active,a.sequence,a.duration,a.test,a.even,a.odd,a.monday,a.tuesday,a.wednesday,a.thursday,a.friday,a.saturday,a.sunday,a.coef,a.rpi from Zone as a left join Sequence as b on a.sequence=b.seq where a.type='zone'",ZONE_PARAMETER_FILE,logger)
        UpdateJson('select * from Parameter limit 1',GLOBAL_PARAMETER_FILE,logger)
        UpdateJson('select * from Sequence where active=1',SEQUENCE_FILE,logger)
        UpdateJson('select id_sv,sv,name,sequence,`order`,open,duration,StartingDate,EndDate from SequenceZone',ZONE_SEQUENCE_FILE,logger)
        UpdateJson('select * from mqtt where active=1',MQTT_BDD_AUTODISCOVERY_FILE,logger)
        PublishMqtt(i,'status/loop_json',logger)
        logger.debug('Boucle Json : '+str(i))
        logger.debug("==============     FIN LOOP            ==============")
        logger.debug("=====================================================")
        time.sleep(1800) #30mins
