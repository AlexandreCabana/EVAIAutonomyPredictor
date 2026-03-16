from random import random, randint
from typing import Annotated
from fastapi import FastAPI, Path, Request, Form, requests
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from sympy import Float


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Base Model exemple
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

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
        roughness_range: int = Form(...)):

    car_info = CarInfo(marque, modele, conduite, is_ac_used)
    env_info = EnvironmentInfo(temperature, meteo, slide_range, roughness_range)
    result =randint(0,1000)/10
    # return FormInfo(car_info, env_info)
    return RedirectResponse(url=f"/result?battery={result}",
                                status_code=status.HTTP_303_SEE_OTHER)

@app.get("/result")
def page_resultat(request: Request, battery: float):
    print(battery)
    return templates.TemplateResponse(
        "resultat.html",
        {"request": request, "battery": battery}
    )
