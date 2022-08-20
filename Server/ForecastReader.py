import requests
import json
from dataclasses import dataclass
from typing import List
from datetime import datetime
import time
import functools

from config import xrapidkey

FORECASTURL = "https://solarenergyprediction.p.rapidapi.com/v2.0/solar/prediction?lat=:lat&lon=:lon&deg=:deg&az=:az&wp=:wp&tech=crystSi"

@dataclass
class ForecastPlane:
    latitude: str
    longitude: str
    degrees: str
    azimuth: str
    wattpeak: str

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
    r = requests.get(
        FORECASTURL.replace(':lat', plane.latitude)
            .replace(':lon', plane.longitude)
            .replace(':deg', plane.degrees)
            .replace(':az', plane.azimuth)
            .replace(':wp', plane.wattpeak),
            headers={
                'X-RapidAPI-Key': xrapidkey,
                'X-RapidAPI-Host': 'solarenergyprediction.p.rapidapi.com'
            }
        )
    jsonDict = r.json()

    watts = jsonDict['output']

    result = {}

    for value in watts:
        newKey = value['timestamp'] / 1000 - 7200
        result[newKey] = value['wh'] / 1000
    
    return result