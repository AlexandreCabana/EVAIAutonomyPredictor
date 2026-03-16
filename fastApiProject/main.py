from typing import Annotated
from fastapi import FastAPI, Path, Request, Form, requests
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

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

# function

@app.put("/items/{item_id}")
async def update_item(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    q: str | None = None,
    item: Item | None = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results

@app.get("/", response_class=HTMLResponse)
async def read_items(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@app.post("/results/")
async def results(
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

    return FormInfo(car_info, env_info)


@app.post("/submit/")
async def submit(name: str = Form(...),last_name: str = Form(...), conduite: str = Form(...)):
    user = User(name,last_name,conduite)
    print(conduite)
    return user

@app.post("/submit_selected")
async def handle_selection(selected_option: Annotated[str, Form()]):
    return {"message": f"You chose : {selected_option}"}

def get_info_from_user(user: User):
    string = ""
    # get length
    string += f"Your first name, {user.name}, contains {len(user.name)} letters and your last name, {user.last_name}, contains {len(user.last_name)} letters"
    return string