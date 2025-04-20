import aiohttp
from weather import WeatherException


async def get_weather(city, API_KEY_WEATHER, units='metric', language='en'):
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={API_KEY_WEATHER}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response_location:
            if response_location.status != 200:
                text = await response_location.text()
                print(f"Ответ от сервера: {text}")
                print(f"Ошибка: {response_location.status}")
                return None
            data = await response_location.json()
        latitude, longitude = data[0]['lat'], data[0]['lon']
        async with session.get(f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY_WEATHER}&units={units}&lang={language}') as response:
            if response.status != 200:
                text = await response.text()
                print(f"Ответ от сервера: {text}")
                print(f"Ошибка: {response.status}")
                return None
            final_data = await response.json()
        return final_data