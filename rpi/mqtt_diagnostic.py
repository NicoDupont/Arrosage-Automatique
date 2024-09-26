"""
* -----------------------------------------------------------------------------------
* Last update :   10/06/2024
* Arrosage Automatique / IrriPi
* Script to update diagnostic key indicator (->push mqtt)
* -----------------------------------------------------------------------------------
"""

from function import ConfigLogging,GetCpuTemperature,GetDiskUsage,GetLoadAverage,GetLocalIp,GetPythonVersion,GetUptime,GetMemoryUsage,PublishMqtt,GetDayTimeNtp,MqttStatusZoneSequence,LoadData,UpdateCoef,GetOsName,MqttProgZone
import yaml
import logging
import time

if __name__ == '__main__':
    #---------------------------------------
    # parameters for the script from config.yaml
    CONFIG_FILE = 'config.yaml'
    with open(CONFIG_FILE) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    ACTIVE_ZONE_FILE = config['p_az_file']            # file of the active zone for lcd
    GLOBAL_SETTINGS_FILE =  config['p_gp_file']      # global parameters for irrigation
    LOG_LEVEL_STREAM = config['p_log_level_stream']   # log level to be write like print  NOTSET | DEBUG | INFO | WARNING | ERROR | CRITICAL
    LOG_LEVEL_FILE = config['p_log_level_file']       # log level to be write in log file  NOTSET | DEBUG | INFO | WARNING | ERROR | CRITICAL
    #--------------------------------------
    #initialise logging config
    #actual_day = GetDayTimeNtp(0,logger)
    logger = logging.getLogger(__name__)#.addHandler(logging.NullHandler())
    #logfile = "log/mqtt_diagnostic_"+str(actual_day.day)+"_"+str(actual_day.month)+"_" +str(actual_day.year)+".txt"
    logfile = "log/mqtt_diagnostic.txt"
    ConfigLogging(logger,logfile,LOG_LEVEL_STREAM,LOG_LEVEL_FILE,True)
    i=0
    while 1==1:
        i+=1
        MODE = LoadData('select * from Parameter limit 1',logger,file=GLOBAL_SETTINGS_FILE)["mode"].iloc[0]
        PublishMqtt(GetOsName(logger),"status/os_name",logger)
        PublishMqtt(GetCpuTemperature(logger),"status/temperature_cpu",logger)
        PublishMqtt(GetDiskUsage(logger),"status/disk_usage",logger)
        PublishMqtt(GetLoadAverage(logger),"status/load_average_cpu",logger)
        PublishMqtt(GetPythonVersion(logger),"status/python_version",logger)
        PublishMqtt(GetUptime(logger),"status/uptime",logger)
        PublishMqtt(GetLocalIp(logger),"status/local_ip",logger)
        PublishMqtt(GetMemoryUsage(logger),"status/memory_usage",logger)
        PublishMqtt("online","status/available",logger) #for availability if use
        MqttStatusZoneSequence(logger) #push mqtt info about zone and sequence to the brocker
        MqttProgZone(logger)
        PublishMqtt(i,'status/loop_diagnostic',logger)
        PublishMqtt(MODE,'status/mode',logger)
        logger.debug('Boucle Diagnostic : '+str(i))
        logger.debug("==============     FIN LOOP          ==============")
        time.sleep(60)
        

