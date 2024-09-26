import logging
logger = logging.getLogger(__name__)#.addHandler(logging.NullHandler())

import calendar
from datetime import datetime, timedelta, date
import requests
import json

API_KEY =  "0624b9f5544bf3786af244248eba3d22"
LATITUDE = 43.82019499614341
LONGITUDE = 5.083383552048545
RAIN_THRESHOLD = 5
# source : https://github.com/markveillette/rpi_sprinkler/tree/master
# Calls open weather history api
def GetPrecipitationByDay(day,logger):
    rain_day = 0
    try:
        API_URL = 'https://api.openweathermap.org/data/3.0/onecall/day_summary?lat={lat}&lon={lon}&date={date}&appid={key}&units=metric&lang=fr'
        weather_history = requests.get(API_URL.format(key=API_KEY,
                                        date=day,
                                        lat=LATITUDE,
                                        lon=LONGITUDE))
        weather_data = json.loads(weather_history.content.decode('utf-8'))
        rain_day = weather_data['precipitation']['total']
        logger.debug(f'Précipitation du jour {date} : {rain_day}')
    except Exception:
        logger.exception('Erreur get_precipitation_history')
    finally:
        return rain_day

def GetTotalPrecipitation(logger, nb_day=2):
    rain_total = 0
    try:
        delta = 1 if datetime.today().hour <4 else 0
        for i in range(0,nb_day+delta):
            day = datetime.today() + timedelta(days=-i) 
            day = day.strftime("%Y-%m-%d")
            print(day)
            rain_total += GetPrecipitationByDay(day,logger)
    except Exception:
        logger.exception('Erreur get_precip_in_window')
    finally:
        return rain_total

rain_history = GetTotalPrecipitation(logger)
print(rain_history) 

#rainfall = get_precip_in_window(logger)
#if rainfall is None:
#    print('%s: Error getting rainfall amount, setting to 0.0 mm\n' % datetime.datetime.now())
#    rainfall = 0.0
#else:
#    print('%s: Rainfall: %f in\n' % (datetime.datetime.now(), rainfall))


#yesterday_timestamp = calendar.timegm((
#      datetime.datetime.utcnow() - \
#      datetime.timedelta(hours=48)).utctimetuple())
#API_URL = 'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={key}&units=metric&lang=fr&exclude=minutely,daily,alerts'
#weather_history = requests.get(API_URL.format(key=API_KEY,
#                                        lat=LATITUDE,
#                                        lon=LONGITUDE))
#print('retour : get_weather_history ')
#print(weather_history.text)