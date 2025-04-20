import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from usersdb import db
from weather.getweather import get_weather
from aiogram.fsm.state import State, StatesGroup
from apikeys.get_apis import get_api
from aiogram.fsm.context import FSMContext

dp = Dispatcher()

class City(StatesGroup):
    city = State()



@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    kb = [[InlineKeyboardButton(text='Get weather', callback_data='weather')], [InlineKeyboardButton(text='Settings', callback_data='settings'), InlineKeyboardButton(text='My balance', callback_data='balance')]]
    await message.answer(f"Hello, {message.from_user.full_name}! My name is WeatherBot⛅\nHow can I help you?🙂 /help", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))
    await db.add_to_db(message.from_user.id)

@dp.message(Command('help'))
async def cmd_help(message: types.Message):
    pass

@dp.callback_query(F.data == 'weather')
async def weather(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Enter your city name')
    await state.set_state(City.city)


@dp.message(City.city)
async def get_city_name(message: types.Message, state: FSMContext):
    await state.update_data(city = message)
    data = await state.get_data()
    weather_data = await get_weather(data['city'].text, get_api()[0])
    await message.answer(f'🏙️ Weather for {weather_data['name']} City:️\n    🌡️ Temperature:️ current {weather_data['main']['temp']}, feels like {weather_data['main']['feels_like']}\n    ⛅ {weather_data['weather'][0]['description'].capitalize()}\n  💨 Wind speed: {weather_data['wind']['speed']}')
    await state.clear()


async def main() -> None:
    token = get_api()[1]
    bot = Bot(token)
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())
