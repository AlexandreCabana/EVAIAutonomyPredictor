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
            "duration": duration
        }

# Form struct
class CarInfo:
    def __init__(self, brand: str, model:str, driving_style: str, is_ac_used: bool):
        self.brand = brand
        self.model = model
        self.driving_style = driving_style
        self.is_ac_used = is_ac_used

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
    start_lng: float
    end_lat: float
    end_lng: float


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@app.post("/submit")
async def submit(
        marque: str = Form(...),
        modele: str = Form(...),
        is_ac_used: bool = Form(False),
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

    car_info = CarInfo(marque, modele, conduite, is_ac_used)
    env_info = EnvironmentInfo(temperature, meteo, slide_range, roughness_range)
    print(car_info, env_info)
    result =randint(0,1000)/10
    # return FormInfo(car_info, env_info)
    return RedirectResponse(url=f"/result?battery={result}",
                                status_code=status.HTTP_303_SEE_OTHER)

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
    return JSONResponse(content=calcul_distance(
        data.start_lat,
        data.start_lng,
        data.end_lat,
        data.end_lng
    ))

if __name__=="__main__":
    uvicorn.run("main:app", reload=True)
