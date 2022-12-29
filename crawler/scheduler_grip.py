import datetime
from rocketry import Rocketry
from rocketry.conds import daily
import threading
import time
import config
from pymongo import MongoClient
from geopy.geocoders import Nominatim
import requests
from db import db, merged_data, unmerged_data
from collections import Counter

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


def get_unmerged_temp(lat: float, lon: float) -> dict:
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
    unmerged = {
        "Yandex": {
            "temp": res_yan["fact"]["temp"],
            "condition": res_yan["fact"]["condition"],
            "pressure_mm": res_yan["fact"]["pressure_mm"],
            "pressure_pa": res_yan["fact"]["pressure_pa"],
            "humidity": res_yan["fact"]["humidity"],
            "feels_like": res_yan["fact"]["feels_like"],
            "wind_dir": res_yan["fact"]["wind_dir"].upper(),
            "wind_speed": res_yan["fact"]["wind_speed"],
        },
        "OpenWeather": {
            "temp": (res_open["main"]["temp_min"] + res_open["main"]["temp_max"]) / 2,
            "condition": res_open["weather"][0]["main"],
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
            "wind_speed": res_vis["days"][0]["windspeed"],  # ? бальные цифры
        },
    }
    return unmerged


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
        "Weather": {
            "temp": (
                (res_vis["days"][0]["tempmax"] + res_vis["days"][0]["tempmin"]) / 2
                + (res_open["main"]["temp_min"] + res_open["main"]["temp_max"]) / 2
                + res_yan["fact"]["temp"]
            )
            / 3,
            "condition": "smth",
            "pressure_mm": (
                res_vis["days"][0]["pressure"] * 0.007501
                + res_open["main"]["pressure"] * 0.007501
                + res_yan["fact"]["pressure_mm"]
            )
            / 3,
            "pressure_pa": (
                res_vis["days"][0]["pressure"]
                + res_open["main"]["pressure"]
                + res_yan["fact"]["pressure_pa"]
            )
            / 3,
            "humidity": (
                res_vis["days"][0]["humidity"]
                + res_open["main"]["humidity"]
                + res_yan["fact"]["humidity"]
            )
            / 3,
            "feels_like": (
                res_vis["days"][0]["feelslike"]
                + res_open["main"]["feels_like"]
                + res_yan["fact"]["feels_like"]
            )
            / 3,
            "wind_dir": Counter(
                [
                    directions[
                        int(round(float(res_vis["days"][0]["winddir"]) / 22.5)) % 16
                    ],
                    directions[int(round(float(res_open["wind"]["deg"]) / 22.5)) % 16],
                    res_yan["fact"]["wind_dir"].upper(),
                ]
            ).most_common(1)[0][0],
            "wind_speed": (
                res_vis["days"][0]["windspeed"]
                + res_open["wind"]["speed"]
                + res_yan["fact"]["wind_speed"]
            )
            / 3,
        },
    }
    return merged


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


def get_preform_russian_cities_and_store_data():
    cities = config.cities
    count_ = 0
    for item in cities.items():
        print("S")
        count_ += 1
        location = item[1]
        merged = get_merged_temp(*location)
        unmerged = get_unmerged_temp(*location)
        print("W")
        merged.setdefault("city", item[0])
        merged.setdefault("date", str(datetime.datetime.today().date()))
        unmerged.setdefault("city", item[0])
        unmerged.setdefault("date", str(datetime.datetime.today().date()))
        print("C")
        merged_data.insert_one(merged)
        print("M")
        unmerged_data.insert_one(unmerged)
        print("U")

    return count_


def get_weather_on_city(city: str):
    location = get_cords_by_city(city)
    print(location)
    merged = get_merged_temp(*location)
    unmerged = get_unmerged_temp(*location)
    print("W")
    merged.setdefault("date", str(datetime.datetime.today().date()))
    merged.setdefault("city", city)
    unmerged.setdefault("city", city)
    unmerged.setdefault("date", str(datetime.datetime.today().date()))
    res = {}
    res.setdefault("merged", merged.copy())
    res.setdefault("unmerged", unmerged.copy())
    print("KKKKKKKKK")
    print(res)
    print("C")
    merged_data.insert_one(merged)
    print("M")
    unmerged_data.insert_one(
        unmerged,
    )
    print("U")
    print("AAAAAAAAAAAAAA")
    print(res)
    return res


app = Rocketry()


@app.task("every 1 day")
async def upload_weather_on_russia():
    print("Started process 'upload_weather_on_russia'")
    get_preform_russian_cities_and_store_data()
    print("Ended process 'upload_weather_on_russia'")


if __name__ == "__main__":
    pass
