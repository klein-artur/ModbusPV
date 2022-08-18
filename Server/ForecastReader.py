import requests
import json
from dataclasses import dataclass
from typing import List
from datetime import datetime
import time
import functools

FORECASTURL = "https://api.forecast.solar/estimate"

@dataclass
class ForecastPlane:
    latitude: str
    longitude: str
    degrees: str
    azimuth: str
    peakKW: str

def sumUpForecasts(left, right):
    result = {}
    for key, value in left.items():
        result[key] = value + right[key]
    return result

def combinedForecasts(planes: List[ForecastPlane]):
    return functools.reduce(
        sumUpForecasts,
        map(lambda plane: readForecast(plane), planes)
    )

def readForecast(plane: ForecastPlane):
    r = requests.get(f"{FORECASTURL}/{plane.latitude}/{plane.longitude}/{plane.degrees}/{plane.azimuth}/{plane.peakKW}")
    jsonDict = r.json()

    watts = jsonDict['result']['watts']

    result = {}

    for date, value in watts.items():
        newKey = int(time.mktime(datetime.strptime(date, '%Y-%m-%d %H:%M:%S').timetuple()))
        result[newKey] = value
    
    return result