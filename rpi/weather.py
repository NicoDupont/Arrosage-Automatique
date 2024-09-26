"""
* -----------------------------------------------------------------------------------
* Last update :   18/06/2024
* Arrosage Automatique / IrriPi
* Script for Openweather map api => A fusionner avec automation
* -----------------------------------------------------------------------------------
"""

from function import ConfigLogging,LoadData,CheckTotalPrecipitation,PublishMqtt
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
    #settings for OpenWeatherMap API
    API_KEY = config['p_api_key_openweatermap']
    LATITUDE = config['p_latitude']
    LONGITUDE = config['p_longitude']
    RAIN_THRESHOLD = config['p_rain_threshold']
    #--------------------------------------
    #initialise logging config
    logger = logging.getLogger(__name__)#.addHandler(logging.NullHandler())
    #logfile = "log/weather_"+str(actual_day.day)+"_"+str(actual_day.month)+"_" +str(actual_day.year)+".txt"
    logfile = "log/weather.txt"
    ConfigLogging(logger,logfile,LOG_LEVEL_STREAM,LOG_LEVEL_FILE,True)
    i=0
    while 1==1: 
        i+=1
        global_settings = LoadData('select * from Parameter limit 1',logger,file=GLOBAL_SETTINGS_FILE)
        PRECIPITATION = global_settings["precipitation"].iloc[0]
        
        #récupération du cumul des précipitations depuis 2 jours et desactivation de l'arrosage si besoin
        #utilise l'api 3.0 openweathermap => besoin d'un compte et d'une keyapi
        CheckTotalPrecipitation(API_KEY,RAIN_THRESHOLD,LATITUDE,LONGITUDE,logger) if PRECIPITATION == 1 else logger.debug('Activation/desactivation de l arrosage selon les precipitations inactif')

        PublishMqtt(i,'status/loop_weather',logger)
        logger.debug('Boucle weather : '+str(i))
        logger.debug("==============     FIN LOOP WEATHER        ==============")
        time.sleep(300) #toutes les 5 minutes (max 1000appels par jour)
        

