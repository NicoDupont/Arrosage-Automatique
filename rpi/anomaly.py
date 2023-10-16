"""
* -----------------------------------------------------------------------------------
* Last update :   12/09/2023
* Irripi
* Anomaly function
* -----------------------------------------------------------------------------------
"""
import time
import pandas as pd
from function import IsAbove,IsTof,IsBelow,TestBdd,CheckPing,IsHst,OpenRelay,LogData,UpdateStatus,Print2Lcd,PublishMqtt

# detect anomlies
def AnomalyDetection(data_n_active,data_zone,data_g_param,ipwebserveur,ipmqtt,rpi_number,date,lcd,lcdscreen,lcdsleep,log,pub_mqtt,debug):
    
    anomaly = False
    # global parameters for irrigation
    for index, row in data_g_param.iterrows():
        mode = row["mode"]
        minp = row["pression_seuil_bas"]
        maxp = row["pression_seuil_haut"]
        canalpupstream = row["pression_canal_amont"]
        canalpdownstream = row["pression_canal_aval"]
        tankpupstream = row["pression_cuve_amont"]
        tankpdownstream = row["pression_cuve_aval"]
        pville = row["pression_ville"]
        pvarrosage = row["pression_arrosage"]
        otp = row["test_pression_cuve"]
        ocp = row["test_pression_canal"]
        ovp = row["test_pression_ville"]
        minh = row["seuil_min_capacite_cuve"]
        height = row["hauteur_eau_cuve"]
        oh = row["test_hauteur_eau_cuve"]
        ws = row["source"]
    
    # --------------------------------
    # Condition tests for watering activation
    dict_ano = {}

    if (IsBelow(canalpupstream,minp) or IsAbove(canalpupstream,maxp)) and IsTof(ocp) == False and ws=="canal":
        dict_ano[1]="Pression Canal Am {} B".format(canalpupstream)

    if (IsBelow(canalpdownstream,minp) or IsAbove(canalpdownstream,maxp))  and IsTof(ocp) == False and ws=="canal":
        dict_ano[1]="Pression Canal Av {} B".format(canalpdownstream)

    if (IsBelow(tankpupstream,minp) or IsAbove(tankpupstream,maxp))  and IsTof(otp) == False and ws=="tank":
        dict_ano[3]="Pression Cuve Am {} B".format(tankpupstream)

    if (IsBelow(tankpdownstream,minp) or IsAbove(tankpdownstream,maxp)) and IsTof(otp) == False and ws=="tank":
        dict_ano[4]="Pression Cuve Av {} B".format(tankpdownstream)

    if (IsBelow(tankpupstream,minp) or IsAbove(tankpupstream,maxp))  and IsTof(ovp) == False and ws=="ville":
        dict_ano[5]="Pression Ville {} B".format(pville)

    if IsAbove(height,minh) == False and IsTof(oh) == False and ws=="tank":
        dict_ano[6]="Niveau Cuve {} L".format(height)

    if mode == 'Hivernage' or mode == 'Stop' :
        dict_ano[7]="Mode Hiver ou Stop"

    if TestBdd(debug) == False:
        dict_ano[8]="BDD Hors Ligne"

    if CheckPing(ipwebserveur,debug) == False:
        dict_ano[9]="WEB Hors Ligne"

    if CheckPing(ipmqtt,debug) == False:
        dict_ano[10]="MQTT : HA Hors Ligne"

    # --------------------------------
    # manage potential anomalies
    blocking_anomaly = 0
    #print(dict_ano)
    if len(dict_ano)>0:
        for error, msg in dict_ano.items():
            if error<8 and blocking_anomaly==0:
                blocking_anomaly = 1
            if debug:
                print("Error Number : ",error," Message : ",msg)
            if lcdscreen:
                Print2Lcd(lcd,lcdsleep,False,"","Erreur Numero : {}".format(error),"{}".format(msg)," ")
            if pub_mqtt:
                PublishMqtt(msg,"ha/arrosage/erreur",debug)
    else:
        if pub_mqtt:
            PublishMqtt('OK',"ha/arrosage/erreur",debug)

    # --------------------------------
    # Deactivation of all the solenoid valves if there is at least one blocking anomaly
    if blocking_anomaly >= 1:
        anomaly = True
        sv = data_zone
        if len(data_n_active.index)>0:
            sv = sv.append(data_n_active, ignore_index=True) 
        print("Anomaly: Deactivation of all solenoid valves")
        for index, row in sv.iterrows():
            gpio = row["gpio"]
            sv = row["sv"]
            open = row["open"]
            rpi_relay = row["rpi"]
            if rpi_number == rpi_relay:
                if IsHst(gpio) == False or open == 1:
                    OpenRelay(gpio,debug)
                    UpdateStatus(sv,0,debug)
                    if log:
                        LogData(date,sv,gpio,'Anomalie','Désactivation',debug)
            time.sleep(0.2) 
    #return true/false
    return anomaly