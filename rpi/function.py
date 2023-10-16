"""
* -----------------------------------------------------------------------------------
* Last update :  05/09/2023
* Irripi
* catalogue de fonction
* -----------------------------------------------------------------------------------
"""

from sqlalchemy import create_engine 
import ntplib
import datetime,time
import pandas as pd
import os
import json
import yaml
import RPi.GPIO as GPIO 
import paho.mqtt.client as mqtt

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

IP_BDD_SERVER = config['p_ip_bdd']
USER_BDD = config['p_user_bdd']
PASSWORD_BDD = config['p_password_bdd']
NAME_DATABASE = config['p_database']
IP_MQTT_BROKER = config['p_ip_mqtt']
USER_MQTT = config['p_user_mqtt']
PASSWORD_MQTT = config['p_password_mqtt']
PORT_MQTT = config['p_port_mqtt']
PUBLISH_MQTT = config['p_mqtt']      

# simple test
def IsAbove(value,threshold):
    if value > threshold:
        return True
    else:
        return False

def IsBelow(value,threshold):
    if value < threshold:
        return True
    else:
        return False

# test yes or no / true or false
def IsTof(value):
    if value == 1 or value == True:
        return True
    else:
        return False

# unit test if gpio is high or low
def IsHst(gpio):
    test= GPIO.input(gpio) 
    if test == 0:
        return False
    else: 
        return True

# start irrigation for the solenoid valve connected to this gpio
def CloseRelay(gpio,debug):
    GPIO.output(gpio, GPIO.LOW)
    if debug:
        print("Close relay : {0}".format(gpio))
    return True

# stop irrigation for the solenoid valve connected to this gpio
def OpenRelay(gpio,debug):
    GPIO.output(gpio, GPIO.HIGH)
    if debug:
        print("Open relay : {0}".format(gpio))
    return True

#number is even or not
def IsEven(x):
    if x % 2 == 0:
        return True
    else:
        return False

#number is odd or not
def IsOdd(x):
    if x % 2 == 0:
        return False
    else:
        return True

# determines if a solenoid valve is within its programming range
def IsInProgrammation(sv,sd,ed,datehour,even,odd,monday,tuesday,wednesday,thursday,friday,saturday,sunday,debug):
    prog = False
    sheduletime = False
    weekday = datehour.isoweekday()
    #print("weekday : "+str(weekday))
    yearday = datehour.timetuple().tm_yday
    #print("yearday : "+str(yearday))
    evenday = IsEven(yearday)
    odday = IsOdd(yearday)
        
    if sd <= datehour <= ed:
        sheduletime = True
    else:
        sheduletime = False
        if debug:
            print("Zone : {}  => not in the time slot".format(sv))
            
    if even == 1 and evenday and sheduletime:
        prog = True
        if debug:
            print("Zone : {}  => in the time slot and even day".format(sv))
    else:
        if odd == 1 and odday and sheduletime:
            prog = True
            if debug:
                print("Zone : {}  => in the time slot and odd day".format(sv))
        else :
            if monday == 1 and weekday == 1 and sheduletime:
                prog = True
                if debug:
                    print("Zone : {}  => in the time slot and monday".format(sv))
            else:
                if tuesday == 1 and weekday == 2 and sheduletime:
                    prog = True
                    if debug:
                        print("Zone : {}  => in the time slot and tuesday".format(sv))
                else: 
                    if wednesday == 1 and weekday == 3 and sheduletime:
                        prog = True
                        if debug:
                            print("Zone : {}  => in the time slot and wednesday".format(sv))
                    else: 
                        if thursday == 1 and weekday == 4 and sheduletime:
                            prog = True
                            if debug:
                                print("Zone : {}  => in the time slot and thursday".format(sv))
                        else: 
                            if friday == 1 and weekday == 5 and sheduletime:
                                prog = True
                                if debug:
                                    print("Zone : {}  => in the time slot and friday".format(sv))
                            else: 
                                if saturday == 1 and weekday == 6 and sheduletime:
                                    prog = True
                                    if debug:
                                        print("Zone : {}  => in the time slot and saturday".format(sv))
                                else: 
                                    if sunday == 1 and weekday == 7 and sheduletime:
                                        prog = True
                                        if debug:
                                            print("Zone : {}  => in the time slot and sunday".format(sv))        
    return prog 

# update of the status of zone
# not work if bdd or nas are not visible on local network
def UpdateStatus(sv,data,debug):
    try:
        if PUBLISH_MQTT: #mqtt first if trouble with the bdd
            PublishMqtt(data,"ha/arrosage/{0}/etat".format(sv),debug)
        db = create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(USER_BDD,PASSWORD_BDD,IP_BDD_SERVER,NAME_DATABASE), pool_recycle=3600)
        bdd = db.connect()
        sql = "update Zone set open={0} where sv='{1}'".format(data,sv)
        bdd.execute(sql)
        bdd.close()
        if debug:
            print("Update Zone : {0} data : {1}".format(sv,data))
        return True
    except:
        if debug:
            print('Update KO : MariaDb Problem @ '+IP_BDD_SERVER)
        return False
    
# "send data to mqtt brocker"
def PublishMqtt(payload,topic,debug):
    try:
        client = mqtt.Client("arrosage") #create new instance
        client.username_pw_set(username=USER_MQTT,password=PASSWORD_MQTT) #set user and password
        client.connect(host=IP_MQTT_BROKER,port=PORT_MQTT) #connect to broker
        client.publish(topic,str(payload)) #publish data to the specified topic
        client.disconnect() #disconnect
        if debug:
            print('Mqtt => Topic : {0} => Payload : {1}'.format(topic,payload))
    except:
        if debug:
            print('Probleme with Mqtt to publish data')

# check if the DATABASE is up
def TestBdd(debug):
    try:
        db = create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(USER_BDD,PASSWORD_BDD,IP_BDD_SERVER,NAME_DATABASE), pool_recycle=3600)
        bdd = db.connect()
        bdd.close
        if debug:
            print('MariaDb OK')
        return True
    except:
        if debug:
            print('MariaDb Problem @ '+IP_BDD_SERVER)
        return False

# check if devices on the local network are up or down
def CheckPing(ip,debug):
    if os.system("ping -c 1 " + ip) == 0:
        if debug:
            print(ip+ " is OK")
        return True
    else:
        if debug:
            print(ip+ " is KO")
        return False

# recovery date and time of the internet or of the rtc module if the internet is not working
def GetDayTimeNtp(nbjour,debug):
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org')
        Internet_date_and_time = datetime.datetime.fromtimestamp(response.tx_time) + datetime.timedelta(days = int(nbjour))
        if debug: 
            print('Internet date and time as reported by NTP server: ',Internet_date_and_time)
        return Internet_date_and_time
    except:
        if debug:
            print('Internet date and time could not be reported by server.')
            print('Date from rtc module')
        return datetime.datetime.today() + datetime.timedelta(days = int(nbjour))


def GetDayTime(nbjour,debug):
    return datetime.datetime.today() + datetime.timedelta(days = int(nbjour))

# load parameters from json file / json files are updated with update_json.py every 1 minute
def GetJsonData(file,debug):
    try:
        # reading the JSON data 
        df = pd.read_json(file)
        df.reset_index(level=0, inplace=True)
        if debug:
            print(df)
            print(file + 'load OK')
        return df
    except:
        if debug:
            print(file + 'load KO')
        return False

# write sequence into a json file
def WriteJsonData(data,file,debug):
    try:
        # write to JSON
        js = data.to_json(orient = 'records')
        parsed = json.loads(js)
        with open(file, 'w') as outfile:
            json.dump(parsed, outfile)
        if debug:
            print(data)
            print(file + 'write OK')
        return True
    except:
        if debug:
            print(file + 'write KO')
        return False

# Log data/events for solenoid valve operation
# not work if bdd or nas are not visible 
def LogData(datehour,sv,gpio,operation,msg,debug):
    try:
        db = create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(USER_BDD,PASSWORD_BDD,IP_BDD_SERVER,NAME_DATABASE), pool_recycle=3600)
        bdd = db.connect()
        sql = "insert into Event (val1,val2,val3,val4) values ('{0}','{1}','{2}','{3}')".format(str(sv),str(gpio),str(operation),str(msg))
        bdd.execute(sql)
        bdd.close()
        if debug:
            print("Log OK  | Date : {0}, SV : {1}, GPIO : {2}, Operation : {3}, Message : {4}".format(datehour,sv,gpio,operation,msg))
        return True
    except:
        if debug:
            print('Log KO : MariaDb Problem @ '+IP_BDD_SERVER)
        return False

# display the active zones on the lcd screen
# works with the column status on the database
# data comes from the last time the json file was updated if the lan network is down
def DisplayActiveZone(file1,lcd,lcdsleep,debug):
    try:
        #part2
        try:
            db = create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(USER_BDD,PASSWORD_BDD,IP_BDD_SERVER,NAME_DATABASE), pool_recycle=3600)
            connection = db.connect()
            sql = "select sz.sv,sz.EndDate,z.open from SequenceZone as sz inner join Zone as z on z.sv=sz.sv where z.open=1 union select sz.sv,sz.EndDate,z.open from SequenceTank as sz inner join Zone as z on z.sv=sz.sv where z.open=1"
            az = pd.read_sql(sql, con=connection)[['sv','open','EndDate']]
            az.reset_index(level=0, inplace=True)
            connection.close
        except:
            # reading the JSON data 
            az = pd.read_json(file1)[['sv','open','EndDate']]
            az.reset_index(level=0, inplace=True)
        
        if not az.empty:
            zones = az['sv'].tolist()
            z = ''
            i=1
            for zone in zones:
                if i==1:
                    z = zone
                else:    
                    z = z + ',' + zone
                i+=1                
            if debug:
                #print('zones : {0}'.format(zones))
                print('zone active : {0}'.format(z))
            lcd.lcd_display_string("Zone Active :       ",3)
            for i in range(1,21-len(z)) :
                z=z+' '
            lcd.lcd_display_string("{0}".format(z),4)
            time.sleep(lcdsleep)

            for index, row in az.iterrows():
                z = "Zone Active : {0}".format(row['sv'])
                for i in range(1,21-len(z)) :
                    z=z+' '
                lcd.lcd_display_string("{0}".format(z),3)
                EndHour = '=> Fin : {0}H{1}'.format(row['EndDate'].hour,row['EndDate'].minute)
                for i in range(1,21-len(EndHour)) :
                    EndHour=EndHour+' '
                lcd.lcd_display_string("{0}".format(EndHour),4)
                time.sleep(lcdsleep)
        else:
            lcd.lcd_display_string("Zone Active :       ",3)
            lcd.lcd_display_string("Aucune              ",4)
            time.sleep(lcdsleep)
            if debug:
                print("no active zone") 


        return True
    except:
        try:
            lcd.lcd_display_string("Zone Active :       ",3)
            lcd.lcd_display_string("-                   ",4)
            time.sleep(lcdsleep)
            if debug:
                print("Problem no active zone")
        except:
            print("erreur DisplayActiveZone")
        
        return False

def UpdateBdd(table,file,truncate,debug):
    try:
        db = create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(USER_BDD,PASSWORD_BDD,IP_BDD_SERVER,NAME_DATABASE), pool_recycle=3600)
        connection = db.connect()
        #truncate table
        if truncate:
            sql = "truncate table {0}".format(table)
            connection.execute(sql)
        # reading the JSON data and insert 
        df = pd.read_json(file)
        if not df.empty:
            if debug:
                print(df.head())
            df['StartingDate'] = pd.to_datetime(df['StartingDate'], unit='ms')
            df['EndDate'] = pd.to_datetime(df['EndDate'], unit='ms')
            #if debug:
            #    print(df.dtypes)
            # insert data
            df.to_sql(table,if_exists='append',index='id_sequence',con=connection,method='multi')
            if debug:
                print('\n')
                print('{0} updated in DATABASE'.format(file))
        else:
            if debug:
                print('\n')
                print('No sequence available for update')
        return True
    except:
        if debug:
            print('\n')
            print('MariaDb Problem @ '+IP_BDD_SERVER)
            print('\n')
            print('{0} not updated in DATABASE'.format(file))
        return False

def UpdateParameter(sql,file,mqtt,topicmqtt,debug):
    try:
        db = create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(USER_BDD,PASSWORD_BDD,IP_BDD_SERVER,NAME_DATABASE), pool_recycle=3600)
        connection = db.connect()
        sv = pd.read_sql(sql, con=connection)
        connection.close
        js = sv.to_json(orient = 'records')
        parsed = json.loads(js)
        #update json file
        with open(file, 'w') as outfile:
            json.dump(parsed, outfile)
        #update mqtt
        #if mqtt:
        #    PublishMqtt(parsed,topicmqtt,debug)
        if debug:
            print('\n')
            print('{0} updated'.format(file))
        return True
    except:
        if debug:
            print('\n')
            print('MariaDb Problem @ '+IP_BDD_SERVER)
            print('\n')
            print('{0} not updated'.format(file))
        return False

def Print2Lcd(lcd,lcdsleep,clear,l1,l2,l3,l4):
    try:
        if clear:
            lcd.lcd_clear()
        if len(l1)>0:
            for i in range(1,21-len(l1)) :
                l1=l1+' '
            lcd.lcd_display_string("{0}".format(l1), 1)
        if len(l2)>0:
            for i in range(1,21-len(l2)) :
                l2=l2+' '
            lcd.lcd_display_string("{0}".format(l2), 2)
        if len(l3)>0:
            for i in range(1,21-len(l3)) :
                l3=l3+' '
            lcd.lcd_display_string("{0}".format(l3), 3)
        if len(l4)>0:
            for i in range(1,21-len(l4)) :
                l4=l4+' '
            lcd.lcd_display_string("{0}".format(l4), 4)
        time.sleep(lcdsleep)
    except:
        print("erreur Print2Lcd")



"""
def UpdateMesure(field,mesure,debug):
    try:
        db = create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(USER_BDD,PASSWORD_BDD,IP_BDD_SERVER,NAME_DATABASE), pool_recycle=3600)
        bdd = db.connect()
        sql = "update Parameter set {0}={1}".format(field,mesure)
        bdd.execute(sql)
        bdd.close()
        print('\n')
        print('Update OK')
        return True
    except: 
        print('\n')
        print('Update KO : MariaDb Problem @ '+IP_BDD_SERVER)
        return False


def InsertMesure(sensor,mesure,debug):
    try:
        db = create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(USER_BDD,PASSWORD_BDD,IP_BDD_SERVER,NAME_DATABASE), pool_recycle=3600)
        bdd = db.connect()
        sql = "insert into Mesure (id_sensor,mesure) values ({0},{1})".format(sensor,mesure)
        bdd.execute(sql)
        bdd.close()
        print('\n')
        print('Insert OK')
        return True
    except: 
        print('\n')
        print('Insert KO : MariaDb Problem @ '+IP_BDD_SERVER)

#not use - convertion is made in the arduino program
def Psi2bar(psi):
    if psi>0 and isinstance(psi, float):
        bar = psi/14.504
    else:
        bar = 0
    return bar


#get data from serial and update/insert data in bdd and publish to mqtt server
def GetSerialData(debug):
    #connection to the arduino nano
    try:
        ser = serial.Serial(port=SERIAL_PORT,baudrate = SERIAL_BAUDRATE,timeout=1)
        ser.flush()
        while ser.inWaiting()==0: pass
        if  ser.inWaiting()>0:           
            dataraw=str(ser.readline(),'utf-8')
            data=dataraw.split("|")

            titprcaam = data[0]
            dataprcaam = data[1]
            titprcaav = data[2]
            dataprcaav = data[3]
            titprcuve = data[4]
            dataprcuve = data[5]
            titwatertemp = data[6]
            datawatertemp = data[7]
            titboxtemp = data[10]
            databoxtemp = data[11]
            tithumitemp = data[8]
            datahumitemp = data[9]

            if debug:
                print('\n')
                print('Raw data : {}'.format(dataraw))
                print("Split data {}".format(data))
                print('Pression Canal Amont : {0} => {1}'.format(titprcaam,float(dataprcaam)))
                print('Pression Canal Aval : {0} => {1}'.format(titprcaav,float(dataprcaav)))
                print('Pression Cuve Aval : {0} => {1}'.format(titprcuve,float(dataprcuve)))
                print('T°C Eau Arrosage : {0} => {1}'.format(titwatertemp,float(datawatertemp)))
                print('Humidite Box Arrosage : {0} => {1}'.format(tithumitemp,float(datahumitemp)))
                print('Temperature Box Arrosage : {0} => {1}'.format(titboxtemp,float(databoxtemp)))
            
            #insert or update in bdd + mqtt
            
            if titprcaam=="canal_pressure_upstream" and isinstance(float(dataprcaam), float):
                UpdateMesure(field, mesure, debug)(titprcaam,float(dataprcaam),debug) #canal 
                InsertMesure(1,float(dataprcaam),debug)
                PublishMqtt(float(dataprcaam),'ha/arrosage/pression_canal_amont',debug) 
            

            if titprcaav=="canal_pressure_downstream" and isinstance(float(dataprcaav), float):
                UpdateMesure(field, mesure, debug)(titprcaav,float(dataprcaav),debug) #canal 
                InsertMesure(1,float(dataprcaav),debug)
                PublishMqtt(float(dataprcaav),'ha/arrosage/pression_canal_aval',debug)            

            if titprcuve=="tank_pressure_downstream" and isinstance(float(dataprcuve), float):
                UpdateMesure(field, mesure, debug)(titprcuve,float(dataprcuve),debug) #tank 
                InsertMesure(1,float(dataprcuve),debug)
                PublishMqtt(float(dataprcuve),'ha/arrosage/pression_cuve_aval',debug)                        

            if titwatertemp=="water_temperature" and isinstance(float(datawatertemp), float):
                UpdateMesure(field, mesure, debug)(titwatertemp,float(datawatertemp),debug)
                InsertMesure(1,float(datawatertemp),debug) 
                PublishMqtt(float(datawatertemp),'ha/arrosage/temperature_eau_arrosage',debug)

            
            if tithumitemp=="box_humidity" and isinstance(float(datahumitemp), float):
                UpdateMesure(field, mesure, debug)(tithumitemp,float(datahumitemp),debug)
                InsertMesure(1,float(datahumitemp),debug) 
                PublishMqtt(float(datahumitemp),'ha/arrosage/box_humidity',debug)
            
            if titboxtemp=="box_temperature" and isinstance(float(databoxtemp), float):
                UpdateMesure(field, mesure, debug)(titboxtemp,float(databoxtemp),debug)
                InsertMesure(1,float(databoxtemp),debug) 
                PublishMqtt(float(databoxtemp),'ha/arrosage/box_temperature',debug)

            if debug:
                print('Mesures Arduino {0} OK'.format(serialport))
    except:
        if debug:
            print('Mesures Arduino {0} KO'.format(serialport))
"""

