from random import random, randint
from typing import Annotated
import requests
import os
from fastapi import FastAPI, Path, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.responses import RedirectResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from sympy import Float
import uvicorn
import json


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Base Model exemple
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

# get elevation data
import requests
import numpy as np
import time

def get_elevation_data(latitude, longitude):
    url = "https://api.open-meteo.com/v1/elevation"
    params = {
        "latitude": latitude,
        "longitude": longitude
    }

    try:
        time.sleep(0.1)
        result = requests.get(url, params=params, timeout=10)
        result.raise_for_status()

        data = result.json()

        if "elevation" in data and len(data["elevation"]) > 0:
            return data["elevation"][0]

        return np.nan

    except (requests.exceptions.RequestException, ValueError, KeyError, IndexError):
        return np.nan

def calcul_distance(lat_i,lon_i,lat_f,lon_f):
#OpenStreetMap
    url = f"http://router.project-osrm.org/route/v1/driving/{lon_i},{lat_i};{lon_f},{lat_f}?overview=full&geometries=geojson"

    response = requests.get(url)
    data = response.json()

    route = data["routes"][0]

    distance = route["distance"]/1000
    duration = route["duration"] /60

    geometry = route["geometry"]["coordinates"]

    # Convert [lng, lat] → [lat, lng]
    route_coords = [[coord[1], coord[0]] for coord in geometry]



    return {
            "route": route_coords,
            "distance": distance,
            "duration": duration,
            "base_duration": duration,
            "traffic_duration": None,
            "traffic_delay": None,
            "provider": "osrm"
        }


def calcul_traffic_route(lat_i, lon_i, lat_f, lon_f):
    api_key = "SQek2X8NbQiiz0wNdweCaLPoHuw0QCEy"
    if not api_key:
        raise Warning("No API key provided")
        return calcul_distance(lat_i, lon_i, lat_f, lon_f)

    locations = f"{lat_i},{lon_i}:{lat_f},{lon_f}"
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{locations}/json"
    params = {
        "key": api_key,
        "traffic": "true",
        "travelMode": "car",
        "routeType": "fastest",
        "routeRepresentation": "polyline",
        "computeTravelTimeFor": "all",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        route = data["routes"][0]
        summary = route["summary"]
        points = route.get("legs", [])[0].get("points", [])
        route_coords = [[point["latitude"], point["longitude"]] for point in points]
        print(summary)
        travel_time_s = summary.get("travelTimeInSeconds")
        no_traffic_s = summary.get("noTrafficTravelTimeInSeconds")
        traffic_delay_s = None
        if travel_time_s is not None and no_traffic_s is not None:
            traffic_delay_s = travel_time_s - no_traffic_s
        else:
            traffic_delay_s = summary.get("trafficDelayInSeconds")

        return {
            "route": route_coords,
            "distance": summary.get("lengthInMeters", 0) / 1000,
            "duration": travel_time_s / 60 if travel_time_s is not None else None,
            "base_duration": no_traffic_s / 60 if no_traffic_s is not None else None,
            "traffic_duration": travel_time_s / 60 if travel_time_s is not None else None,
            "traffic_delay": traffic_delay_s / 60 if traffic_delay_s is not None else None,
            "provider": "tomtom",
        }
    except requests.RequestException:
        return calcul_distance(lat_i, lon_i, lat_f, lon_f)


def get_meteo(lat, lon, date = None, heure :int = None):
    url = "https://api.open-meteo.com/v1/forecast"
    mode = "hourly" if date is not None and heure is not None else "current"
    params = {
        "latitude": lat,
        "longitude": lon,
        mode: [
            "temperature_2m",
            "weather_code",
            "cloud_cover",
            "precipitation",
            "wind_speed_10m",
            "is_day",
        ],
        "timezone": "auto",
        "start_date": date,
        "end_date": date
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if date is not None and heure is not None:

        hourly = data.get("hourly", {})
        weather_code = hourly.get("weather_code")[heure]
        meteo = weather_code_to_meteo(weather_code)
        return {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone"),
            "time": hourly.get("time")[heure],
            "temperature": hourly.get("temperature_2m")[heure],
            "meteo": meteo,
            "cloud_cover": hourly.get("cloud_cover")[heure],
            "precipitation": hourly.get("precipitation")[heure],
        }
    else:
        current = data.get("current", {})
        weather_code = current.get("weather_code")
        meteo = weather_code_to_meteo(weather_code)
        return {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone"),
            "time": current.get("time"),
            "temperature": current.get("temperature_2m"),
            "meteo": meteo,
            "cloud_cover": current.get("cloud_cover"),
            "precipitation": current.get("precipitation"),
            "overall_forecast": data
        }

def weather_code_to_meteo(weather_code):
    if weather_code == 0:
        meteo = "soleil"
    elif weather_code in {1, 2, 3, 45, 48}:
        meteo = "nuageux"
    elif weather_code in {71, 73, 75, 77, 85, 86}:
        meteo = "neige"
    else:
        meteo = "pluie"
    return meteo


# Form struct
class CarInfo:
    def __init__(self, brand: str, model: str, driving_style: str, ac_target_temperature: int):
        self.brand = brand
        self.model = model
        self.driving_style = driving_style
        self.ac_target_temperature = ac_target_temperature
class EnvironmentInfo:
    def __init__(self, temperature: str, meteo:str, chaussee: int, rougness: int):
        self.temp = temperature
        self.meteo = meteo
        self.chaussee = chaussee

class FormInfo:
    def __init__(self, carInfo : CarInfo, environmentInfo : EnvironmentInfo):
        self.carInfo = carInfo
        self.environmentInfo = environmentInfo

class User:
    def __init__(self, name, last_name, driving_style):
        self.name = name
        self.last_name = last_name
        self.driving_style = driving_style

class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float


class MeteoRequest(BaseModel):
    lat: float
    lon: float
    date: str | None = None
    heure: int | None = None


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@app.post("/submit")
async def submit(
        marque: str = Form(...),
        modele: str = Form(...),
        ac_target_temperature: int = Form(22),
        conduite: str = Form(...),
        temperature: str = Form(...),
        meteo: str = Form(...),
        slide_range: int = Form(...),
        roughness_range: int = Form(...),
        start_lat: float = Form(...),
        start_lng: float = Form(...),
        end_lat: float = Form(...),
        end_lng: float = Form(...)
):
    route_data = calcul_distance(start_lat, start_lng, end_lat, end_lng)
    distance = route_data["distance"]
    duration = route_data["duration"]
    altitude_start = get_elevation_data(start_lat, start_lng)
    altitude_end = get_elevation_data(end_lat, end_lng)
    delta_elevation = altitude_end-altitude_start
    slope = delta_elevation/(distance*1000)

    car_info = CarInfo(marque, modele, conduite, ac_target_temperature)
    env_info = EnvironmentInfo(temperature, meteo, slide_range, roughness_range)

    with open("model.json", 'r') as file:
        data = json.load(file)
        current_settings = data["2000"]["functions"]
        params_names = ["speedAvg", "slope", "temperature", "total_distance"]
        params_values = [distance/(duration/60), slope, float(temperature), distance]
        somme = 0
        for i, param_name in enumerate(params_names):
            current_values = current_settings[param_name]
            current_param_value = params_values[i]
            somme += calculate_param(current_values, current_param_value)
        print(somme)

    print(car_info, env_info)
    result = randint(0, 1000) / 10
    return RedirectResponse(url=f"/result?battery={result}", status_code=status.HTTP_303_SEE_OTHER)

def calculate_param(param_value : dict,value):
    somme = 0
    for i, param in enumerate(reversed(list(param_value[list(param_value.keys())[0]].values()))):
        somme += param*value**i
    return somme


@app.get("/result")
def page_resultat(request: Request, battery: float, distance: float | None = None,
    duration: float | None = None):
    print(battery)
    return templates.TemplateResponse(
        request=request,
        name="resultat.html",
        context={
            "battery": battery,
            "distance": distance,
            "duration": duration
        }
    )
@app.post("/route")
async def get_route(data: RouteRequest):
    print("get route called")
    return JSONResponse(content=calcul_traffic_route(
        data.start_lat,
        data.start_lon,
        data.end_lat,
        data.end_lon
    ))

@app.post("/meteo")
async def meteo(data: MeteoRequest):
    if data.date is not None and data.heure is not None:
        return JSONResponse(content=get_meteo(data.lat, data.lon, data.date, data.heure))
    else:
        return JSONResponse(content=get_meteo(data.lat, data.lon))

if __name__=="__main__":
    uvicorn.run("main:app", reload=True)
