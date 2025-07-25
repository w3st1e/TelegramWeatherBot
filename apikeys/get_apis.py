import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="apikeys.env")  # Загружает переменные из .env

def get_api():
    weatherapi = os.getenv("WEATHER_API")
    token = os.getenv("TELEGRAM_TOKEN")
    return [weatherapi, token]
