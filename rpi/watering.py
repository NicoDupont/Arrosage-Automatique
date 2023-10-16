"""
* -----------------------------------------------------------------------------------
* Last update :   12/09/2023
* Irripi
* Part managing the opening or closing of the solenoid valves
* -----------------------------------------------------------------------------------
"""

import  time
from function import IsTof,IsHst,CloseRelay,OpenRelay,IsInProgrammation,UpdateStatus,LogData,Print2Lcd
#import lcddriver 

def Watering(iteration,data_n_active,data_zone,data_g_param,rpi_number,date,debug,log,lcd,lcdscreen,lcdsleep,name,version,dateversion):
    
    #if lcdscreen:
    #    lcd = lcddriver.lcd()
    
    data_active = data_zone  
  
    # global parameters for irrigation
    for index, row in data_g_param.iterrows():
        test_duration = row["duree_test"]
        mode = row["mode"]
    
    if 1==1:    
        # --------------------------------
        # --------------------------------
        # deactivation of solenoid valves which are not in the sequence / active
        if lcdscreen:
            Print2Lcd(lcd,lcdsleep,True,"{0} {1} {2}".format(name,version,dateversion),"Desactivation Zone :","Zones Non Active","")

        for index, row in data_n_active.iterrows():
            sv = row["sv"]
            gpio = row["gpio"]
            rpi_relay = row["rpi"]
            open = row["open"]
            # if solenoid valve is open :
            if rpi_number == rpi_relay:
                if IsHst(gpio) == False or open == 1:
                    UpdateStatus(sv,0,debug) 
                    if not data_active.empty:
                        OpenRelay(gpio,debug)
                        if log:
                            LogData(date,sv,gpio,'Non Active','Désactivation',debug)
                        print("Deactivation of the non-active solenoid valve : "+sv)
                        #time.sleep(0.5)                  
                                           
        # --------------------------------
        # Deactivation of all solenoid valves on 1st launch / if restart unexpectedly  
        if iteration == 1:
            if lcdscreen:
                Print2Lcd(lcd,lcdsleep,False,"","1er demarrage :","Desactivation Zone :","Zone Active : - ")           
            for index, row in data_active.iterrows():
                gpio = row["gpio"]
                sv = row["sv"]
                rpi_relay = row["rpi"]
                open = row["open"]
                if rpi_number == rpi_relay:
                    if IsHst(gpio) == False or open == 1:
                        OpenRelay(gpio,debug)
                        UpdateStatus(sv,0,debug) 
                        if log:
                            LogData(date,sv,gpio,'First Start','Désactivation',debug)
                        print("Deactivation of the solenoid valve on first start: "+sv)
                        #time.sleep(0.5)

        # --------------------------------
        # --------------------------------
        # --------------------------------
        #main part open / close relay 
        else:
        # test operation
            if mode == 'Test':
                print("-------------------------------")
                print("test operation :")
                if lcdscreen:
                    Print2Lcd(lcd,lcdsleep,False,"","Mode : Test"," "," ")
                
                for index, row in data_active.iterrows():
                    gpio = row["gpio"]
                    sv = row["sv"]
                    rpi_relay = row["rpi"]
                    open = row["open"]
                    if rpi_number == rpi_relay:
                        # force desactivation of all solenoids
                        if IsHst(gpio) == False or open == 1:
                            OpenRelay(gpio,debug)
                            UpdateStatus(sv,0,debug) 
                            if log:
                                LogData(date,sv,gpio,'Test','Désactivation',debug)
                            #time.sleep(0.5)
                
                for index, row in data_active.iterrows():
                    gpio = row["gpio"]
                    sv = row["sv"]
                    rpi_relay = row["rpi"]
                    open = row["open"]
                    if rpi_number == rpi_relay:
                        if IsHst(gpio) == True:
                            CloseRelay(gpio,debug)
                            UpdateStatus(sv,1,debug)
                            if lcdscreen:
                                lcd.lcd_display_string(" Zone Active : {0} ".format(sv), 3)
                                Print2Lcd(lcd,lcdsleep,False,"","Mode : Test","Zone Active : {0}".format(sv),"Pour {0} secondes".format(test_duration))
                            if log:
                                LogData(date,sv,gpio,'Test','Activation',debug) 
                            print("Test Solenoid : {0} for {1} seconds".format(sv,test_duration))
                        time.sleep(test_duration)
                        OpenRelay(gpio,debug)
                        UpdateStatus(sv,0,debug) 
                        
                        if lcdscreen:
                            lcd.lcd_display_string(" Zone Active : - ", 3)
                            Print2Lcd(lcd,lcdsleep,False,"","Mode : Test","Zone Active : --"," ")
                        if log:
                            LogData(date,sv,gpio,'Test','Désactivation',debug)
                        #time.sleep(0.5)
  
            else:
                # --------------------------------
                # Manual operation :
                if mode == 'Manuel' or mode == 'Domotique':
                    if lcdscreen:
                        Print2Lcd(lcd,lcdsleep,False,"","Mode : Manuel"," "," ")
                    for index, row in data_active.iterrows():
                        gpio = row["gpio"]
                        sv = row["sv"]
                        open = row["open"]
                        rpi_relay = row["rpi"]                       
                        if rpi_number == rpi_relay:
                            # close sv
                            if IsHst(gpio) == False and IsTof(open) == False:
                                if not data_active.empty:
                                    OpenRelay(gpio,debug)
                                    UpdateStatus(sv,0,debug)
                                    if log:
                                        LogData(date,sv,gpio,'Manuel','Désactivation',debug)   
                                time.sleep(0.5)
                                print("Manual deactivation Solenoid valve : "+sv)
                            # log sv already open    
                            if IsHst(gpio) == False and IsTof(open) == True:
                                #CloseRelay(gpio,debug)
                                #UpdateStatus(sv,1,debug) 
                                #time.sleep(0.5)
                                print("Solenoid valve already opened manually : "+sv)
                            # open sv    
                            if IsHst(gpio) == True and IsTof(open) == True:
                                time.sleep(0.5)
                                CloseRelay(gpio,debug)
                                UpdateStatus(sv,1,debug)
                                if log:
                                    LogData(date,sv,gpio,'Manuel','Activation',debug)
                                print("Manual activation Solenoid valve : "+sv)
                    
                # --------------------------------
                # --------------------------------
                # Automatic operation
                else: 
                    if mode == 'Auto':
                        if lcdscreen:
                            Print2Lcd(lcd,lcdsleep,False,"","Mode : Automatique"," "," ")  
                        for index, row in data_active.iterrows():
                            gpio = row["gpio"]
                            open = row["open"]
                            sv = row["sv"]
                            sd = row["StartingDate"]
                            ed = row["EndDate"]
                            even = row["even"]
                            odd = row["odd"]
                            monday = row["monday"]
                            tuesday = row["tuesday"]
                            wednesday = row["wednesday"]
                            thursday = row["thursday"]
                            friday = row["friday"]
                            saturday = row["saturday"]
                            sunday = row["sunday"]
                            rpi_relay = row["rpi"]

                            if rpi_number == rpi_relay:
                                InProgrammation = IsInProgrammation(sv,sd,ed,date,even,odd,monday,tuesday,wednesday,thursday,friday,saturday,sunday,debug)
                                # close sv
                                if IsHst(gpio) == False and InProgrammation == False:
                                    if not data_active.empty or open == 1:
                                        OpenRelay(gpio,debug)
                                        UpdateStatus(sv,0,debug) 
                                        if log:
                                            LogData(date,sv,gpio,'Auto','Désactivation',debug) 
                                    time.sleep(0.5)
                                    print("Solenoid valve programming deactivation : "+sv)
                                # sv already open 
                                if IsHst(gpio) == False and InProgrammation == True :
                                    #CloseRelay(gpio,debug)
                                    #UpdateStatus(sv,1,debug) 
                                    #time.sleep(0.2)
                                    print("Solenoid valve already open : "+sv)
                                # open sv
                                if IsHst(gpio) == True and InProgrammation == True :
                                    time.sleep(0.5)
                                    CloseRelay(gpio,debug)
                                    UpdateStatus(sv,1,debug)
                                    if log:
                                        LogData(date,sv,gpio,'Auto','Activation',debug)
                                    print("Solenoid valve programming activation : "+sv) 