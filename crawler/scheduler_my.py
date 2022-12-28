from rocketry import Rocketry
from rocketry.conds import daily
import threading
import time
import config
from pymongo import MongoClient
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="my_app")

client = MongoClient(config.db_connection)
db = client['Weather']

cities = config.cities

def get_cords_by_city(city:str) -> tuple:
    location = geolocator.geocode(city)
    return location[1]


def get_yandex_weather(lat: float, lon:float):
    pass


def get_open_weather(lat: float, lon:float):
    pass


def get_crossing(lat: float, lon:float):
    pass


def get_yandex_weather(city: str):
    pass


def get_open_weather(city: str):
    pass


def get_crossing(city: str):
    pass



def get_city_weather(city: str):
    pass


def get_preform_russian_cities():
    pass

# app = Rocketry()


# @app.task("every 2 min")
# async def do_things():

#     print('P1')
    
if __name__ == '__main__':
    pass 