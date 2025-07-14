import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from usersdb import db
from weather.getweather import get_weather
from aiogram.fsm.state import State, StatesGroup
from apikeys.get_apis import get_api

dp = Dispatcher()

class City(StatesGroup):
    city = State()



@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    en_kb = [[InlineKeyboardButton(text='Get weather', callback_data='weather')], [InlineKeyboardButton(text='Settings', callback_data='settings'), InlineKeyboardButton(text='My balance', callback_data='balance')]]
    ru_kb = [[InlineKeyboardButton(text='Получить погоду', callback_data='weather')], [InlineKeyboardButton(text='Настройки', callback_data='settings'), InlineKeyboardButton(text='Мой баланс', callback_data='balance')]]
    kb = en_kb if await db.get_lang(message.from_user.id) == 'en' else ru_kb
    if await db.get_lang(message.from_user.id) =='en':
        await message.answer(f"Hello, {message.from_user.full_name}! My name is WeatherBot⛅\nHow can I help you?🙂 /help", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))
    else:
        await message.answer(f"Привет, {message.from_user.full_name}! Меня зовут WeatherBot⛅\nКак я могу помочь вам?🙂 /help", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))
    await db.add_to_db(message.from_user.id, balance=5)

@dp.message(Command('help'))
async def cmd_help(message: types.Message):
    pass


@dp.message(Command('lang'))
async def cmd_lang(message: types.Message):
    if await db.get_lang(message.from_user.id) == 'en':
        await db.set_lang(message.from_user.id, 'ru')
        await message.answer('Язык успешно изменен на русский')
    else:
        await db.set_lang(message.from_user.id, 'en')
    await message.answer('Language updated successfully')
@dp.callback_query(F.data == 'weather')
async def weather(callback: types.CallbackQuery, state: FSMContext):
    if await db.get_balance(callback.from_user.id) <= 0:
        if await db.get_lang(callback.from_user.id) == 'ru':
            await callback.message.answer('У вас недостаточно вызовов для получения погоды. Пополните баланс.')
        else:
            await callback.message.answer("You don't have enough calls to get the weather. Please recharge your balance.")
    else:
        if await db.get_lang(callback.from_user.id) == 'ru':
            await callback.message.answer('Введите название вашего города')
        else:
            await callback.message.answer('Enter your city name')
        await state.set_state(City.city)

@dp.callback_query(F.data == 'balance')
async def get_balance(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balance = await db.get_balance(user_id)
    if await db.get_lang(user_id) == 'ru':
        await callback.message.answer(f'Ваш баланс: {balance} вызовов')
    await callback.message.answer(f'Your balance: {balance} calls')


@dp.message(City.city)
async def get_city_name(message: types.Message, state: FSMContext):
    await state.update_data(city=message)
    data = await state.get_data()
    weather_data = await get_weather(data['city'].text, get_api()[0])
    if await db.get_lang(message.from_user.id) == 'ru':
        await message.answer(f'🏙️ Погода для города {weather_data["name"]}:\n    🌡️ Температура: текущая {weather_data["main"]["temp"]}, ощущается как {weather_data["main"]["feels_like"]}\n    ⛅ {weather_data["weather"][0]["description"].capitalize()}\n  💨 Скорость ветра: {weather_data["wind"]["speed"]}')
    else:
        await message.answer(f'🏙️ Weather for {weather_data['name']} City:️\n    🌡️ Temperature:️ current {weather_data['main']['temp']}, feels like {weather_data['main']['feels_like']}\n    ⛅ {weather_data['weather'][0]['description'].capitalize()}\n  💨 Wind speed: {weather_data['wind']['speed']}')
    await db.change_balance(message.from_user.id, await db.get_balance(message.from_user.id) - 1)
    await state.clear()

@dp.callback_query(F.data == 'settings')
async def settings(callback: types.CallbackQuery):
    if await db.get_lang(callback.from_user.id) == 'ru':
        await callback.message.answer('Выберите действие:', reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Изменить язык', callback_data='change_language')], [InlineKeyboardButton(text='Пополнить баланс', callback_data='recharge_balance')]]))
    else:
        await callback.message.answer('Choose an action:', reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Change language', callback_data='change_language')], [InlineKeyboardButton(text='Recharge balance', callback_data='recharge_balance')]]))


@dp.callback_query(F.data == 'change_language')
async def change_language(callback: types.CallbackQuery):
    if await db.get_lang(callback.from_user.id) == 'ru':
        await db.set_lang(callback.from_user.id, 'en')
        await callback.message.answer('Language changed to English successfully')
    else:
        await db.set_lang(callback.from_user.id, 'ru')
        await callback.message.answer('Язык успешно изменен на русский')
@dp.callback_query(F.data == 'recharge_balance')
async def recharge_balance(callback: types.CallbackQuery):
    await db.change_balance(callback.from_user.id, 5)
    if await db.get_lang(callback.from_user.id) == 'ru':
        await callback.message.answer('Ваш баланс успешно пополнен на 5 вызовов.')
    else:
        await callback.message.answer('Your balance has been successfully recharged with 5 calls.')


async def main() -> None:
    token = get_api()[1]
    bot = Bot(token)
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())
