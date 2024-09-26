"""
* -----------------------------------------------------------------------------------
* Last update :   17/06/2024
* Arrosage Automatique / IrriPi
* Function managing the opening or closing of solenoid valves (via gpio)
* -----------------------------------------------------------------------------------
"""

import time
from function import IsTof,IsHst,CloseRelay,OpenRelay,IsProgrammed,UpdateStatus,LogDatabase

def Watering(iteration,critical_anomaly,zone_inactive,zone_active,global_settings,rpi_number,actual_date,logger) -> None:
    
    # global parameters for irrigation
    test_duration = global_settings["duree_test"].iloc[0]
    mode = global_settings["mode"].iloc[0]
    
    for index, row in zone_inactive.iterrows():
        sv = row["sv"]
        gpio = row["gpio"]
        rpi_relay = row["rpi"]
        open = row["open"]
        # if solenoid valve is open :
        if rpi_number == rpi_relay:
            if IsHst(gpio) == False or open == 1:
                UpdateStatus(sv,0,logger) 
                if not zone_active.empty:
                    OpenRelay(gpio,logger)
                    LogDatabase(sv,gpio,'Non Active','Désactivation','sv',logger)
                    logger.debug("Deactivation of the non-active solenoid valve : "+sv)
                                           
    # --------------------------------
    # Deactivation of all solenoid valves on 1st launch / if restart unexpectedly  or criticval anomaly detected
    if iteration == 1 or mode in ['Stop','Hivernage'] or critical_anomaly == True:         
        for index, row in zone_active.iterrows():
            gpio = row["gpio"]
            sv = row["sv"]
            rpi_relay = row["rpi"]
            sv_state = row["open"]
            if rpi_number == rpi_relay:
                if IsHst(gpio) == False or sv_state == 1:
                    OpenRelay(gpio,logger)
                    UpdateStatus(sv,0,logger) 
                    if iteration==1:
                        text1 = 'First Start'
                        text2 = 'Deactivation of the solenoid valve on first start : '
                    else: 
                        if critical_anomaly:
                            text1 = 'Critical Anomaly'
                            text2 = 'Deactivation of the solenoid valve on Critical Anomaly : '
                        else:
                            if mode in ['Stop','Hivernage']:
                                text1 = 'Stop'
                                text2 = 'Deactivation of the solenoid valve on Stop Mode : '
                    LogDatabase(sv,gpio,text1,'Désactivation','sv',logger)
                    logger.info(text2+sv)
    else:

        if mode == 'Test':
            logger.info("Start Test Mode")
            #Tout desactiver avant test
            for index, row in zone_active.iterrows():
                gpio = row["gpio"]
                sv = row["sv"]
                rpi_relay = row["rpi"]
                sv_state = row["open"]
                if rpi_number == rpi_relay:
                    if IsHst(gpio) == False and IsTof(sv_state) == False:
                        OpenRelay(gpio,logger)
                        UpdateStatus(sv,0,logger) 
                        LogDatabase(sv,gpio,"Test",'1st Désactivation','sv',logger) 
                        logger.info("Désactivation : {0} avant test".format(sv)) 
                        time.sleep(1)       
            for index, row in zone_active.iterrows():
                gpio = row["gpio"]
                sv = row["sv"]
                rpi_relay = row["rpi"]
                sv_state = row["open"]
                if rpi_number == rpi_relay:
                    if IsHst(gpio) == True:
                        CloseRelay(gpio,logger)
                        UpdateStatus(sv,1,logger)
                        LogDatabase(sv,gpio,'Test','Activation','sv',logger) 
                        logger.info("Test Solenoid : {0} for {1} seconds".format(sv,test_duration))
                    time.sleep(test_duration)
                    OpenRelay(gpio,logger)
                    UpdateStatus(sv,0,logger) 
                    LogDatabase(sv,gpio,'Test','Désactivation','sv',logger)
                    time.sleep(0.1)
            logger.info("Ending Test Mode") 
    

        if mode in ['Manuel','Domotique']:
            for index, row in zone_active.iterrows():
                gpio = row["gpio"]
                sv = row["sv"]
                sv_state = row["open"]
                rpi_relay = row["rpi"]                       
                if rpi_number == rpi_relay:
                    if IsHst(gpio) == False and IsTof(sv_state) == False:
                        if not zone_active.empty:
                            OpenRelay(gpio,logger)
                            UpdateStatus(sv,0,logger)
                            LogDatabase(sv,gpio,'Manuel','Désactivation','sv',logger) 
                            logger.info("Manual deactivation Solenoid valve : "+sv)      
                            time.sleep(1)
                    # log sv already open    
                    if IsHst(gpio) == False and IsTof(sv_state) == True:
                        logger.debug("Solenoid valve already opened manually : "+sv) 
                    # open sv    
                    if IsHst(gpio) == True and IsTof(sv_state) == True:
                        time.sleep(1)
                        CloseRelay(gpio,logger)
                        UpdateStatus(sv,1,logger)
                        LogDatabase(sv,gpio,'Manuel','Activation','sv',logger)
                        logger.info("Manual activation Solenoid valve : "+sv)
                        

        if mode in ['Auto','Demande']:
            for index, row in zone_active.iterrows():
                gpio = row["gpio"]
                sv_state = row["open"]
                sv = row["sv"]
                rpi_relay = row["rpi"]
                if rpi_number == rpi_relay:
                    InProgrammation = IsProgrammed(sv,row["StartingDate"],row["EndDate"],actual_date,row["even"],row["odd"],row["monday"],row["tuesday"],row["wednesday"],row["thursday"],row["friday"],row["saturday"],row["sunday"],False,logger)
                    # close sv
                    if IsHst(gpio) == False and InProgrammation == False:
                        if not zone_active.empty or sv_state == 1:
                            OpenRelay(gpio,logger)
                            UpdateStatus(sv,0,logger) 
                            LogDatabase(sv,gpio,'Auto','Désactivation','sv',logger) 
                            logger.info("Solenoid valve programming deactivation : "+sv)
                            time.sleep(1)
                    # sv already open 
                    if IsHst(gpio) == False and InProgrammation == True :
                        logger.debug("Solenoid valve already open : "+sv)
                    # open sv
                    if IsHst(gpio) == True and InProgrammation == True :
                        time.sleep(1)
                        CloseRelay(gpio,logger)
                        UpdateStatus(sv,1,logger)
                        LogDatabase(sv,gpio,'Auto','Activation','sv',logger)
                        logger.info("Solenoid valve programming activation : "+sv) 
