import aiohttp
from weather import WeatherException

async def get_latlon(city, API_KEY_WEATHER):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city}&&appid={API_KEY_WEATHER}') as response_location:
            if response_location.status == 200:
                return await response_location.json()
            else:
                raise WeatherException

async def get_weather(latitude, longitude, city, API_KEY_WEATHER, units='metric', language='en'):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY_WEATHER}&units={units}&lang={language}') as response:
            if response.status == 200:
                return await response.json()
            else:
                raise WeatherException