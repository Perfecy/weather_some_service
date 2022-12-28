from rocketry import Rocketry
from rocketry.conds import daily
import threading
import time
import config
from pymongo import MongoClient
from geopy.geocoders import Nominatim
import requests
from db import db, merged_data, unmerged_data

geolocator = Nominatim(user_agent="my_app")


cities = config.cities


def get_cords_by_city(city: str) -> tuple:
    location = geolocator.geocode(city)
    return location[1]


def get_yandex_weather(lat: float, lon: float) -> dict:
    return requests.get(
        config.yandex_api.format(lat, lon), headers=config.yandex_header
    ).json()


def get_open_weather(lat: float, lon: float) -> dict:
    return requests.get(
        config.open_weather_api.format(lat, lon, config.open_weather_api_key)
    ).json()


def get_vis_crossing_weather(lat: float, lon: float) -> dict:
    return requests.get(config.vis_crossing_api.format(lat, lon)).json()


# TODO
def get_openmeteo(lat: float, lon: float):
    pass


def get_merged_temp(lat: float, lon: float) -> dict:
    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    res_yan = get_yandex_weather(lat, lon)
    res_open = get_open_weather(lat, lon)
    res_vis = get_vis_crossing_weather(lat, lon)
    merged = {
        "Yandex": {
            "temp": res_yan["fact"]["temp"],
            "condition": "smth",
            "pressure_mm": res_yan["fact"]["pressure_mm"],
            "pressure_pa": res_yan["fact"]["pressure_pa"],
            "humidity": res_yan["fact"]["humidity"],
            "feels_like": res_yan["fact"]["feels_like"],
            "wind_dir": res_yan["fact"]["wind_dir"],
            "wind_speed": res_yan["fact"]["wind_speed"],
        },
        "OpenWeather": {
            "temp": (res_open["main"]["temp_min"] + res_open["main"]["temp_max"]) / 2,
            "condition": "smth",
            "pressure_mm": res_open["main"]["pressure"] * 0.007501,
            "pressure_pa": res_open["main"]["pressure"],
            "humidity": res_open["main"]["humidity"],
            "feels_like": res_open["main"]["feels_like"],
            "wind_dir": directions[
                int(round(float(res_open["wind"]["deg"]) / 22.5)) % 16
            ],
            "wind_speed": res_open["wind"]["speed"],
        },
        "VisualCrossing": {
            "temp": (res_vis["days"][0]["tempmax"] + res_vis["days"][0]["tempmin"]) / 2,
            "condition": "smth",
            "pressure_mm": res_vis["days"][0]["pressure"] * 0.007501,
            "pressure_pa": res_vis["days"][0]["pressure"],
            "humidity": res_vis["days"][0]["humidity"],
            "feels_like": res_vis["days"][0]["feelslike"],
            "wind_dir": directions[
                int(round(float(res_vis["days"][0]["winddir"]) / 22.5)) % 16
            ],
            "wind_speed": res_vis["days"][0]["winddir"],  # ? бальные цифры
        },
    }


# def get_yandex_weather(city: str):
#     location = get_cords_by_city(city=city)
#     return get_yandex_weather(*location)


# def get_open_weather(city: str):
#     location = get_cords_by_city(city=city)
#     return get_open_weather(*location)


# def get_vis_crossing_weather(city: str):
#     location = get_cords_by_city(city=city)
#     return get_vis_crossing_weather(*location)


# def get_city_weather(city: str):
#     pass


def get_preform_russian_cities():
    cities = config.cities
    for item in cities.items():
        print(item)
    pass


# app = Rocketry()


# @app.task("every 2 min")
# async def do_things():


if __name__ == "__main__":
    pass
