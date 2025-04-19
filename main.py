import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from usersdb import db
from weather.getweather import get_latlon, get_weather
from aiogram.fsm.state import State, StatesGroup
from apikeys.get_apis import get_api

dp = Dispatcher()


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    kb = [[InlineKeyboardButton(text='Get weather', callback_data='weather')], [InlineKeyboardButton(text='Settings', callback_data='settings'), InlineKeyboardButton(text='My balance', callback_data='balance')]]
    await message.answer(f"Hello, {message.from_user.full_name}! My name is WeatherBot⛅\nHow can I help you?🙂 /help", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))
    await db.add_to_db(message.from_user.id)

@dp.message(Command('help'))
async def cmd_help(message: types.Message):
    pass

@dp.callback_query(F.data == 'weather')
async def weather(callback: types.CallbackQuery):
    all_data = await get_latlon('Moscow', get_api()[0])
    all_data = await get_weather(all_data[0]['lat'], all_data[0]['lon'], 'Moscow', get_api()[0])
    await callback.message.answer(f'🏙️ Weather for {all_data['name']} City:️\n    🌡️ Temperature:️ current {all_data['main']['temp']}, feels like {all_data['main']['feels_like']}\n    ⛅ {all_data['weather'][0]['description'].capitalize()}\n  💨 Wind speed: {all_data['wind']['speed']}')



async def main() -> None:
    token = get_api()[1]
    bot = Bot(token)
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())
