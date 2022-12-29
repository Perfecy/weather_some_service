from fastapi import FastAPI
from scheduler_grip import app as app_rocketry, get_weather_on_city
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

app = FastAPI()
session = app_rocketry.session


@app.get("/get_weather_on_city")
async def check_workin(city):
    res = get_weather_on_city(city)
    json_compatible_item_data = jsonable_encoder(res)
    return JSONResponse(content=json_compatible_item_data)


@app.get("/tasks")
async def get_tasks():
    return session.tasks


@app.post("/my-route")
async def manipulate_session():
    for task in session.tasks:
        print("P2")
        pass
    return True
