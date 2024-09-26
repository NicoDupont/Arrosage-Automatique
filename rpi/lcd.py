"""
* -----------------------------------------------------------------------------------
* Last update :  10/06/2024
* Arrosage Automatique / IrriPi
* Displaying information on the 20x4 LCD (need alert and lcd reboot)
* -----------------------------------------------------------------------------------
"""
import lcddriver  #comment if not lcd
import yaml
#from sqlalchemy import create_engine 
#import pandas as pd
from function import Print2Lcd,DisplayActiveZone,ConfigLogging,GetDayTime,LoadData,GetDayTime,PublishMqtt,DisplaySequence
from anomaly import AnomalyDetection
import logging
import time

#---------------------------------------
if __name__ == '__main__':
    #---------------------------------------
    # parameters for the script from config.yaml
    CONFIG_FILE = 'config.yaml'
    with open(CONFIG_FILE) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        #print(config)
    GLOBAL_SETTINGS_FILE =  config['p_gp_file']      # global settings for irrigation
    ACTIVE_ZONE_FILE = config['p_az_file']            # file of the active zone for lcd
    ACTIVE_LCD = config['p_lcd_screen']               # use or not the lcd
    PROJECT_NAME = config['p_name']                   # name of the project
    PROJECT_VERSION = config['p_version']             # version number of the project
    PROJECT_DATE_VERSION = config['p_date_version']   # date version of the project
    WAIT_TIME_LCD = config['p_lcd_sleep_time']        # time in seconds to keep display
    LOG_LEVEL_STREAM = config['p_log_level_stream']   # log level to be write like print  NOTSET | DEBUG | INFO | WARNING | ERROR | CRITICAL
    LOG_LEVEL_FILE = config['p_log_level_file']       # log level to be write in log file  NOTSET | DEBUG | INFO | WARNING | ERROR | CRITICAL
    RPI_NUMBER =  config['p_rpi']                     # if I need more than one rpi to manage all solenoid valves
    IP_WEB_SERVER =  config['p_ip_web']               # ip web server                
    IP_MQTT_SERVER =  config['p_ip_mqtt']             # ip mqtt server              
    IP_HA_SERVER =  config['p_ip_ha']             # ip mqtt server
    IP_WEB =  config['p_ip_www']                  # ip for test internet   
    
    #--------------------------------------
    #initialise logging config
    actual_day = GetDayTime(0)
    logger = logging.getLogger(__name__)#.addHandler(logging.NullHandler())
    #logfile = "log/lcd"+str(actual_day.day)+"_"+str(actual_day.month)+"_" +str(actual_day.year)+".txt"
    logfile = "log/lcd.txt"
    ConfigLogging(logger,logfile,LOG_LEVEL_STREAM,LOG_LEVEL_FILE,True)
    
    if ACTIVE_LCD:
        #initialise the lcd screen
        try:
            lcd = lcddriver.lcd()
        except Exception:
            logger.exception("Probleme initialisation du lcd")
        Print2Lcd(lcd,WAIT_TIME_LCD,True,"{0} {1} {2}".format(PROJECT_NAME,PROJECT_VERSION,PROJECT_DATE_VERSION),"Demarrage !","","",logger) 
        Print2Lcd(lcd,WAIT_TIME_LCD,False,"","Initialisation..."," "," ",logger) 
        i=0
        while 1==1:
            i+=1
            Print2Lcd(lcd,WAIT_TIME_LCD,True,"","Mise a jour :","Parametres"," ",logger) 
            actual_day = GetDayTime(0)
            global_settings = LoadData('select * from Parameter limit 1',logger,file=GLOBAL_SETTINGS_FILE)
            kpi_auto_coef = global_settings['kpi_auto_coef'].iloc[0] if global_settings['auto_coef'].iloc[0]==1 else "none"
            auto_coef = "OUI" if global_settings['auto_coef'].iloc[0]==1 else "NON"
            anomaly = AnomalyDetection(global_settings,IP_WEB_SERVER,IP_HA_SERVER,IP_MQTT_SERVER,IP_WEB,logger)
            critique = "OUI" if anomaly[0] and anomaly[1] else "NON"
            Print2Lcd(lcd,WAIT_TIME_LCD,True,"Date : ","{0}-{1}-{2} {3}:{4}".format('0'+str(actual_day.day) if actual_day.day<10 else actual_day.day,'0'+str(actual_day.month) if actual_day.month<10 else actual_day.month,actual_day.year,'0'+str(actual_day.hour) if  actual_day.hour<10 else actual_day.hour,'0'+str(actual_day.minute) if  actual_day.minute<10 else actual_day.minute),"","",logger)
            if anomaly[0]:
                Print2Lcd(lcd,WAIT_TIME_LCD,True,f"Nb Erreur : {str(len(anomaly[2]))}","Erreur Critique : ",critique,"",logger)
                Print2Lcd(lcd,WAIT_TIME_LCD,True,"Liste Anomalie :","","","",logger)
                for error, msg in anomaly[2].items():
                    Print2Lcd(lcd,WAIT_TIME_LCD,True,f"Erreur numero : {str(error)}","Message =>",msg,"",logger)
            Print2Lcd(lcd,WAIT_TIME_LCD,True,"Calcul Auto Coef :",auto_coef,"Methode :",kpi_auto_coef,logger)
            Print2Lcd(lcd,WAIT_TIME_LCD,True,"Arrosage",f"Mode : {global_settings['mode'].iloc[0]}","","",logger) 
            DisplaySequence(lcd,WAIT_TIME_LCD,logger)
            DisplayActiveZone(lcd,WAIT_TIME_LCD,logger)
            PublishMqtt(i,'status/loop_lcd',logger)
            logger.debug('Boucle lcd : '+str(i))
            logger.debug("==============     FIN LOOP LCD      ==============")
            time.sleep(15)