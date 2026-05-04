import os
from pathlib import Path
from random import randint

import pandas as pd
import requests
import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sympy import Float
import uvicorn
import json
import csv
# get elevation data
import requests
import numpy as np
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory of the current file
BASE_DIR = Path(__file__).resolve().parent
MODEL_JSON_PATH = BASE_DIR / "model.json"
CAR_INFO_CSV = BASE_DIR / "static" / "car_info.csv"

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


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

    response = requests.get(url, timeout=10)
    data = response.json()

    route = data["routes"][0]

    distance = route["distance"]/1000
    duration = route["duration"] /60 #sans traffic

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
        "provider": "osrm",
    }


def calcul_traffic_route(lat_i, lon_i, lat_f, lon_f):
    api_key = "SQek2X8NbQiiz0wNdweCaLPoHuw0QCEy" #S'il vous plait garder cette clée privée
    if not api_key:
        raise Warning("No API key provided")

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


def weather_code_to_meteo(weather_code):
    if weather_code == 0:
        return "soleil"
    if weather_code in {1, 2, 3, 45, 48}:
        return "nuageux"
    if weather_code in {71, 73, 75, 77, 85, 86}:
        return "neige"
    return "pluie"


def get_meteo(lat, lon, date = None, heure :int = None):
    # obtient la météo avec openMeteo selon localisation et date
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
def get_vehicle_data(marque: str, modele: str):
    result = df_cars[
        (df_cars["-- brand --"].astype(str).str.strip().str.lower() == marque.strip().lower())
        & (df_cars["model"].astype(str).str.strip().str.lower() == modele.strip().lower())
    ]
    return None if result.empty else result.iloc[0].to_dict()

def get_ac_power(marque: str, modele: str, temperature: str, duration:float, ac_target_temperature:float):
    atm_pressure = 101.34 #kPa
    gas_constant = 8.314
    molar_mass_air = 28.96 #mol
    specific_heat_air = 1.012 #kJ/(kg*K)
    kelvins_offset = 273.15

    car_data = get_vehicle_data(marque, modele)
    length_mm = float(car_data["length_mm"])
    width_mm = float(car_data["width_mm"])
    height_mm = float(car_data["height_mm"])
    car_volume_percentage = 0.2  # rough first estimate for a car
    ambient_temperature = float(temperature)
    duration_sec = duration * 60
    heat_loss_coefficient = 120  # W/K, rough first estimate for a car

    car_volume = ((length_mm * width_mm * height_mm) / 1_000_000) * car_volume_percentage  # L
    car_air_quantity = (atm_pressure * car_volume) / (gas_constant * (ambient_temperature + kelvins_offset))  # mol, loi des gaz parfaits
    car_air_mass = car_air_quantity * molar_mass_air / 1000  # kg
    delta_temperature = abs(ac_target_temperature - ambient_temperature)
    ac_energy = car_air_mass * specific_heat_air * delta_temperature  # kJ, Q=m*c*deltaT
    ac_power = ac_energy / duration_sec  # kW

    ac_loss = (heat_loss_coefficient * delta_temperature) / 1000  # kW
    ac_power += ac_loss

    print(
        {
            "duration_sec": duration_sec,
            "car_volume_l": car_volume,
            "car_air_mass": car_air_mass,
            "ac_energy": ac_energy,
            "ac_power": ac_power,
        })

    return ac_power



df_cars = pd.read_csv(CAR_INFO_CSV, encoding="utf-8-sig")

# Form struct
class CarInfo:
    def __init__(self, brand: str, model: str, driving_style: str, ac_target_temperature: int):
        self.brand = brand
        self.model = model
        self.driving_style = driving_style
        self.ac_target_temperature = ac_target_temperature


class EnvironmentInfo:
    def __init__(self, temperature: str, meteo: str):
        self.temp = temperature
        self.meteo = meteo


class FormInfo:
    def __init__(self, car_info: CarInfo, environment_info: EnvironmentInfo):
        self.carInfo = car_info
        self.environmentInfo = environment_info


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
    return templates.TemplateResponse(request=request, name="index.html")

def get_vehicle_data(marque: str, modele: str):
    result = df_cars[
        (df_cars["-- brand --"].astype(str).str.strip().str.lower() == marque.strip().lower())
        & (df_cars["model"].astype(str).str.strip().str.lower() == modele.strip().lower())
    ]
    return None if result.empty else result.iloc[0].to_dict()



@app.post("/submit")
async def submit(
    request: Request,
    marque: str = Form(...),
    modele: str = Form(...),
    ac_target_temperature: int = Form(21),
    current_charge_percentage: float = Form(100),
    conduite: str = Form(...),
    temperature: str = Form(...),
    meteo: str = Form(...),
    start_lat: float | None = Form(None),
    start_lng: float | None = Form(None),
    end_lat: float | None = Form(None),
    end_lng: float | None = Form(None),
    duration: float | None = Form(None),
):
    # Vérification des champs

    params = [marque, modele, ac_target_temperature, current_charge_percentage, conduite, temperature, meteo,
              start_lat, start_lng, end_lat, end_lng, duration]  # Liste tes champs critiques
    if any(v is None or v == "" for v in params):
        # On recharge la page index.html avec un message d'erreur
        # Utilise cette syntaxe pour éviter l'erreur "unhashable type: dict"
        return templates.TemplateResponse(
            request=request,  # L'argument request est obligatoire
            name="index.html",
            context={
                "error_msg": "Certains paramètres ont mal été définis ou aucun trajet n'a été sélectionné"
            }
        )
    if current_charge_percentage < 0 or current_charge_percentage > 100:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error_msg": "La charge actuelle du vehicule doit etre comprise entre 0 et 100%."
            }
        )
    route_data = calcul_distance(start_lat, start_lng, end_lat, end_lng)

    if duration is None:
        duration = route_data["duration"]
    distance = route_data["distance"]
    duration = route_data["duration"]
    altitude_start = get_elevation_data(start_lat, start_lng)
    altitude_end = get_elevation_data(end_lat, end_lng)
    delta_elevation = altitude_end-altitude_start
    slope = delta_elevation/(distance*1000)
    speedAvg = distance/(duration/60)

    ac_power = get_ac_power(marque, modele, temperature, duration, ac_target_temperature)

    car_info = CarInfo(marque, modele, conduite, ac_target_temperature)
    env_info = EnvironmentInfo(temperature, meteo)

    with MODEL_JSON_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)
        current_settings = data["88965"]["functions"]
        params_names = ["speedAvg", "slope", "temperature"]
        params_values = [speedAvg, slope, float(temperature)]
        somme = 0
        for i, param_name in enumerate(params_names):
            current_values = current_settings[param_name]
            current_param_value = params_values[i]
            somme += calculate_param(current_values, current_param_value)
        # somme : W/km
        energy_consumption = round(somme*distance,3)

    # trouver la capacité de la batterie
    total_battery_capacity = float(fetch_ev_batteryCapacity(modele)) * 1000
    battery_capacity = total_battery_capacity * (current_charge_percentage / 100)
    pourcentage_used = round(energy_consumption / total_battery_capacity * 100, 2)

    predicted_range = int(battery_capacity / energy_consumption) if energy_consumption > 0 else 0
    return RedirectResponse(
        url=(
            f"/result?range={predicted_range}"
            f"&pourcentage_used={pourcentage_used}"
            f"&energy_consumption={energy_consumption}"
        ),
        status_code=status.HTTP_303_SEE_OTHER,
    )

def fetch_ev_batteryCapacity(car_model):
    with CAR_INFO_CSV.open("r", encoding="utf-8-sig", newline="") as file:
        csvFile = csv.reader(file)
        for line in csvFile:
            if car_model in line:
                return line[3]
        return None


def calculate_param(param_value : dict,value):
    somme = 0
    for i, param in enumerate(reversed(list(param_value[list(param_value.keys())[0]].values()))):
        somme += param*value**i
    return somme


@app.get("/result")
@app.get("/range")
def page_resultat(request: Request, range: float, pourcentage_used: float, energy_consumption:float, distance: float | None = None, duration: float | None = None):
    print(range)
    return templates.TemplateResponse(
        request=request,
        name="resultat.html",
        context={
            "range": range,
            "distance": distance,
            "duration": duration,
            "pourcentage_used": pourcentage_used,
            "energy_consumption": energy_consumption
        },
    )


@app.post("/route")
async def get_route(data: RouteRequest):
    print("get route called")
    return JSONResponse(
        content=calcul_traffic_route(
            data.start_lat,
            data.start_lon,
            data.end_lat,
            data.end_lon,
        )
    )


@app.post("/meteo")
async def meteo(data: MeteoRequest):
    if data.date is not None and data.heure is not None:
        return JSONResponse(content=get_meteo(data.lat, data.lon, data.date, data.heure))
    return JSONResponse(content=get_meteo(data.lat, data.lon))


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
