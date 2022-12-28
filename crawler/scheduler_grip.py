from rocketry import Rocketry
from rocketry.conds import daily
import threading
import time
import config
from pymongo import MongoClient
from geopy.geocoders import Nominatim
import requests
from db import merged_data, unmerged_data

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


def get_crossing(lat: float, lon: float):
    return requests.get(config.vis_crossing_api.format(55.75222, 37.61556)).json()


def get_openmeteo(lat: float, lon: float):
    pass


# def get_yandex_weather(city: str):
#     location = get_cords_by_city(city=city)
#     return get_yandex_weather(*location)


# def get_open_weather(city: str):
#     location = get_cords_by_city(city=city)
#     return get_open_weather(*location)


# def get_crossing(city: str):
#     location = get_cords_by_city(city=city)
#     return get_crossing(*location)


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
