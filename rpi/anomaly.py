"""
* -----------------------------------------------------------------------------------
* Last update :   17/06/2024
* Arrosage Automatique / IrriPi
* Anomaly function
* -----------------------------------------------------------------------------------
"""
import time
import pandas as pd
from function import IsAbove,IsTof,IsBelow,TestDatabase,CheckPing,IsHst,PublishMqtt,LogDatabase,CheckZoneOrder,CheckSequenceTime
import logging

# detect anomlies
def AnomalyDetection(global_settings: pd.DataFrame,ip_webserveur: str,ip_ha: str,ip_mqtt: str,ip_web: str,logger) -> tuple:
    try:
        # global parameters for irrigation
        mode = global_settings["mode"].iloc[0]
        minp = global_settings["pression_seuil_bas"].iloc[0]
        maxp = global_settings["pression_seuil_haut"].iloc[0]
        canalpupstream = global_settings["pression_canal_amont"].iloc[0]
        canalpdownstream = global_settings["pression_canal_aval"].iloc[0]
        tankpupstream = global_settings["pression_cuve_amont"].iloc[0]
        tankpdownstream = global_settings["pression_cuve_aval"].iloc[0]
        pville = global_settings["pression_ville"].iloc[0]
        pvarrosage = global_settings["pression_arrosage"].iloc[0]
        otp = global_settings["test_pression_cuve"].iloc[0]
        ocp = global_settings["test_pression_canal"].iloc[0]
        ovp = global_settings["test_pression_ville"].iloc[0]
        minh = global_settings["seuil_min_capacite_cuve"].iloc[0]
        height = global_settings["hauteur_eau_cuve"].iloc[0]
        oh = global_settings["test_hauteur_eau_cuve"].iloc[0]
        ws = global_settings["source"].iloc[0]

        # --------------------------------
        # Condition tests for watering activation
        dict_anomaly = {}

        if (IsBelow(canalpupstream,minp) or IsAbove(canalpupstream,maxp)) and IsTof(ocp) == False and ws=="canal":
            dict_anomaly[1]="Pression Canal Am {} B".format(canalpupstream)

        if (IsBelow(canalpdownstream,minp) or IsAbove(canalpdownstream,maxp))  and IsTof(ocp) == False and ws=="canal":
            dict_anomaly[1]="Pression Canal Av {} B".format(canalpdownstream)

        if (IsBelow(tankpupstream,minp) or IsAbove(tankpupstream,maxp))  and IsTof(otp) == False and ws=="tank":
            dict_anomaly[3]="Pression Cuve Am {} B".format(tankpupstream)

        if (IsBelow(tankpdownstream,minp) or IsAbove(tankpdownstream,maxp)) and IsTof(otp) == False and ws=="tank":
            dict_anomaly[4]="Pression Cuve Av {} B".format(tankpdownstream)

        if (IsBelow(tankpupstream,minp) or IsAbove(tankpupstream,maxp))  and IsTof(ovp) == False and ws=="ville":
            dict_anomaly[5]="Pression Ville {} B".format(pville)

        if IsAbove(height,minh) == False and IsTof(oh) == False and ws=="tank":
            dict_anomaly[6]="Niveau Cuve {} L".format(height)

        if mode == 'Stop' :
            dict_anomaly[7]="Mode Stop"

        if CheckPing(ip_web,logger) == False:
            dict_anomaly[9]="Internet Offline"

        if CheckPing(ip_webserveur,logger) == False:
            dict_anomaly[10]="WEB Offline"

        if CheckZoneOrder(logger) == True:
            dict_anomaly[11]="Nb Zone Active"

        #if CheckSequenceTime(logger) == True:
        #    dict_anomaly[12]="Ano Debut / Fin"

        if TestDatabase(logger) == False:
            dict_anomaly[20]="Database Offline"

        if CheckPing(ip_mqtt,logger) == False:
            dict_anomaly[21]="Brocker Mqtt Offline"
        
        if CheckPing(ip_ha,logger) == False:
            dict_anomaly[22]="HomeAssistant Offline"

        # --------------------------------
        # manage potential anomalies
        anomaly = False
        critical_anomaly = False

        if len(dict_anomaly)>0:
            anomaly = True
            logger.debug("liste des erreurs :")
            for error, msg in dict_anomaly.items():
                LogDatabase(error,msg,'','','ano',logger)
                if error>=20:
                    critical_anomaly = True
                    logger.error("Critical Anomaly : "+str(error)+" Message : "+str(msg))
                else:
                    logger.warning("Error Number : "+str(error)+" Message : "+str(msg))     
                    
        result = [anomaly,critical_anomaly,dict_anomaly]
    except Exception:
        logger.exception('Erreur Anomaly Detection')
        LogDatabase('Erreur','Anomaly Detection','','','ano',logger)
        result = [False,False,{}]
    finally:
        return result


def MqttStatusAnomaly(anomaly: tuple,logger) -> None:
    try:
        if anomaly[0] or anomaly[1]:
            e = 0
            ec = 0
            for error, msg in anomaly[2].items():
                if error<20:
                    e+=1
                else:
                    ec+=1
            PublishMqtt('{0}'.format(e),"status/nb_erreur",logger)
            PublishMqtt('{0}'.format(ec),"status/nb_erreur_critique",logger)
            if anomaly[0]:
                PublishMqtt('1',"status/erreur",logger)
            if anomaly[1]:        
                PublishMqtt('1',"status/erreur_critique",logger)
        else:
            PublishMqtt('0',"status/erreur",logger)
            PublishMqtt('0',"status/erreur_critique",logger)
            PublishMqtt('0',"status/nb_erreur",logger)
            PublishMqtt('0',"status/nb_erreur_critique",logger)
    except Exception:
        logger.exception('Erreur MqttAnomaly')
        LogDatabase('Erreur','MqttAnomaly','','','ano',logger)