"""
* -----------------------------------------------------------------------------------
* Last update :   18/06/2024
* Arrosage Automatique / IrriPi
* Script for integrate automation
* -----------------------------------------------------------------------------------
"""

from function import ConfigLogging,UpdateCoef,PublishMqtt,LoadData,UpdateZoneOrder,UpdateSequenceTime
import yaml
import logging
import time

if __name__ == '__main__':
    #---------------------------------------
    # parameters for the script from config.yaml
    CONFIG_FILE = 'config.yaml'
    with open(CONFIG_FILE) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    GLOBAL_SETTINGS_FILE =  config['p_gp_file']      # global parameters for irrigation
    LOG_LEVEL_STREAM = config['p_log_level_stream']   # log level to be write like print  NOTSET | DEBUG | INFO | WARNING | ERROR | CRITICAL
    LOG_LEVEL_FILE = config['p_log_level_file']       # log level to be write in log file  NOTSET | DEBUG | INFO | WARNING | ERROR | CRITICAL
    #settings for compute auto coef
    MIN_TEMP = config['p_min_coef_temp']
    MAX_TEMP = config['p_max_coef_temp']
    MIN_COEF = config['p_min_coef']
    MAX_COEF = config['p_max_coef']

    #--------------------------------------
    #initialise logging config
    #actual_day = GetDayTimeNtp(0,logger)
    logger = logging.getLogger(__name__)#.addHandler(logging.NullHandler())
    #logfile = "log/automation_"+str(actual_day.day)+"_"+str(actual_day.month)+"_" +str(actual_day.year)+".txt"
    logfile = "log/automation.txt"
    ConfigLogging(logger,logfile,LOG_LEVEL_STREAM,LOG_LEVEL_FILE,True)
    i=0
    while 1==1:
        
        i+=1
       
        global_settings = LoadData('select * from Parameter limit 1',logger,file=GLOBAL_SETTINGS_FILE)
        AUTO_COEF = global_settings["auto_coef"].iloc[0]
        KPI_AUTO_COEF = global_settings["kpi_auto_coef"].iloc[0]
        SEQUENCE_HOUR = global_settings["verif_seq_hour"].iloc[0]
        
        # maj du coef selon un kpi => calcul lineaire
        UpdateCoef(MIN_TEMP,MAX_TEMP,MIN_COEF,MAX_COEF,KPI_AUTO_COEF,logger) if AUTO_COEF == 1 else logger.debug('Auto Coef inactif')
        
        #updates the order of zones if too many zones can be active at the same time (power supply limit for sv and also the pump)
        #iterates until there are no more active zones compared to the maximum number available in operation at the same time
        # only work on individual sequence actualy
        while True:
            res = UpdateZoneOrder(logger)
            if res == False: 
                break
        #change start hour of a sequence if the complete sequence from start to the end is between 2 days
        #UpdateSequenceTime(logger) if SEQUENCE_HOUR == 1 else logger.debug('Modification Debut sequence inactive')
        
        PublishMqtt(i,'status/loop_automation',logger)
        logger.debug('Boucle Automation : '+str(i))
        logger.debug("==============     FIN LOOP AUTOMATION        ==============")
        time.sleep(120)
        

