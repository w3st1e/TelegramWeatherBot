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
    en_kb = [[InlineKeyboardButton(text='⛅ Get weather', callback_data='weather')], [InlineKeyboardButton(text='⚙️ Settings', callback_data='settings'), InlineKeyboardButton(text='📊 My balance', callback_data='balance')]]
    ru_kb = [[InlineKeyboardButton(text='⛅ Получить данные о погоде', callback_data='weather')], [InlineKeyboardButton(text='⚙️ Настройки', callback_data='settings'), InlineKeyboardButton(text='📊 Мой баланс', callback_data='balance')]]
    kb = en_kb if await db.get_lang(message.from_user.id) == 'en' else ru_kb
    if await db.get_lang(message.from_user.id) =='en':
        await message.answer(f"👋 Hello, <b>{message.from_user.full_name}</b>! ⛅ My name is WeatherBot\n🤗 How can I help you?", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb), parse_mode='HTML')
    else:
        await message.answer(f"👋 Привет, <b>{message.from_user.full_name}</b>! ⛅ Меня зовут WeatherBot\n🤗 Как я могу помочь вам?", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb), parse_mode='HTML')
    await db.add_to_db(message.from_user.id, balance=5)


@dp.message(Command('lang'))
async def cmd_lang(message: types.Message):
    if await db.get_lang(message.from_user.id) == 'en':
        await db.set_lang(message.from_user.id, 'ru')
        kb = types.InlineKeyboardMarkup(inline_keyboard=[InlineKeyboardButton(text='🔙 Вернуться назад', callback_data='back_to_start')])
        await message.edit_text('✅ Язык успешно изменен на русский', reply_markup=kb)
    else:
        kb = types.InlineKeyboardMarkup(inline_keyboard=[InlineKeyboardButton(text='🔙 Back', callback_data='back_to_start')])
        await db.set_lang(message.from_user.id, 'en')
        await message.edit_text('✅ Language updated successfully', reply_markup=kb)

@dp.callback_query(F.data == 'weather')
async def weather(callback: types.CallbackQuery, state: FSMContext):
    if await db.get_balance(callback.from_user.id) <= 0:
        if await db.get_lang(callback.from_user.id) == 'ru':
            kb = types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='⚡ Пополнить баланс', callback_data='recharge_balance'), InlineKeyboardButton(text='🔙 Вернуться назад', callback_data='back_to_start')]])
            await callback.message.edit_text('❗ У вас недостаточно вызовов для получения данных о погоде. Пополните баланс', reply_markup=kb)
        else:
            kb = types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Recharge balance💳', callback_data='recharge_balance'), InlineKeyboardButton(text='Back🔙', callback_data='back_to_start')]])
            await callback.message.edit_text("❗ You don't have enough calls to get the weather. Please recharge your balance", reply_markup=kb)
    else:
        if await db.get_lang(callback.from_user.id) == 'ru':
            await callback.message.edit_text('📍 Введите название города, о котором хотите получить данные о погоде')
        else:
            await callback.message.edit_text('📍 Enter city name, which you wan to get weather data for')
        await state.set_state(City.city)

@dp.callback_query(F.data == 'balance')
async def get_balance(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balance = await db.get_balance(callback.from_user.id)
    if await db.get_lang(user_id) == 'ru':
        kb = types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔙 Вернуться назад', callback_data='back_to_start')]])
        await callback.message.edit_text(f'📊 Ваш баланс: {balance} вызовов', reply_markup=kb)
    else:
        kb = types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔙 Back', callback_data='back_to_start')]])
        await callback.message.edit_text(f'📊 Your balance: {balance} calls', reply_markup=kb)


@dp.message(City.city)
async def get_city_name(message: types.Message, state: FSMContext):
    await state.update_data(city=message)
    data = await state.get_data()
    weather_data = await get_weather(data['city'].text, get_api()[0])
    if not weather_data:
        if await db.get_lang(message.from_user.id) == 'ru':
            await message.answer('❗ Не удалось получить данные о погоде. Проверьте правильность введенного города.', reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔙 Вернуться назад', callback_data='back_to_start')]]))
        else:
            await message.answer('❗ Failed to get weather data. Please check the city name.', reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔙 Back', callback_data='back_to_start')]]))
    else:
        if await db.get_lang(message.from_user.id) == 'ru':
            kb = types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔙 Вернуться назад', callback_data='back_to_start')]])
            await message.answer(f'🏙️ Погода для города <b>{message.text}</b>:\n    🌡️ Температура: текущая {weather_data["main"]["temp"]}, ощущается как {weather_data["main"]["feels_like"]}\n    ⛅ {weather_data["weather"][0]["description"].capitalize()}\n  💨 Скорость ветра: {weather_data["wind"]["speed"]}', reply_markup=kb, parse_mode='HTML')
        else:
            kb = types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔙 Back', callback_data='back_to_start')]])
            await message.answer(f'🏙️ Weather for <b>{message.text}</b> City:️\n    🌡️ Temperature:️ current {weather_data['main']['temp']}, feels like {weather_data['main']['feels_like']}\n    ⛅ {weather_data['weather'][0]['description'].capitalize()}\n  💨 Wind speed: {weather_data['wind']['speed']}', reply_markup=kb, parse_mode='HTML')
        await db.change_balance(message.from_user.id, await db.get_balance(message.from_user.id) - 1)
        await state.clear()

@dp.callback_query(F.data == 'settings')
async def settings(callback: types.CallbackQuery):
    if await db.get_lang(callback.from_user.id) == 'ru':
        await callback.message.edit_text('Выберите действие:', reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🌐 Изменить язык', callback_data='change_language'), InlineKeyboardButton(text='📊 Пополнить счет', callback_data='recharge_balance')], [InlineKeyboardButton(text='Вернуться назад🔙', callback_data='back_to_start')]]))
    else:
        await callback.message.edit_text('Choose an action:', reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🌐 Change language', callback_data='change_language'), InlineKeyboardButton(text='📊 Recharge', callback_data='recharge_balance')], [InlineKeyboardButton(text='Back🔙', callback_data='back_to_start')]]))


@dp.callback_query(F.data == 'change_language')
async def change_language(callback: types.CallbackQuery):
    if await db.get_lang(callback.from_user.id) == 'ru':
        kb = types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Back🔙', callback_data='back_to_start')]])
        await db.set_lang(callback.from_user.id, 'en')
        await callback.message.edit_text('✅ Language changed to English successfully', reply_markup=kb)
    else:
        kb = types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Вернуться назад🔙', callback_data='back_to_start')]])
        await db.set_lang(callback.from_user.id, 'ru')
        await callback.message.edit_text('✅ Язык успешно изменен на русский', reply_markup=kb)

@dp.callback_query(F.data == 'recharge_balance')
async def recharge_balance(callback: types.CallbackQuery):
    await db.change_balance(callback.from_user.id, 5)
    if await db.get_lang(callback.from_user.id) == 'ru':
        kb = types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Вернуться назад🔙', callback_data='back_to_start')]])
        await callback.message.edit_text('✅ Ваш баланс успешно пополнен на 5 вызовов.', reply_markup=kb)
    else:
        kb = types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Back🔙', callback_data='back_to_start')]])
        await callback.message.edit_text('✅ Your balance has been successfully recharged with 5 calls.', reply_markup=kb)

@dp.callback_query(F.data == 'back_to_start')
async def back_to_start(callback: types.CallbackQuery):
    en_kb = [[InlineKeyboardButton(text='⛅ Get weather', callback_data='weather')], [InlineKeyboardButton(text='⚙️ Settings', callback_data='settings'), InlineKeyboardButton(text='📊 My balance', callback_data='balance')]]
    ru_kb = [[InlineKeyboardButton(text='⛅ Получить данные о погоде', callback_data='weather')], [InlineKeyboardButton(text='⚙️ Настройки', callback_data='settings'), InlineKeyboardButton(text='📊 Мой баланс', callback_data='balance')]]
    kb = en_kb if await db.get_lang(callback.message.from_user.id) == 'en' else ru_kb
    if await db.get_lang(callback.message.from_user.id) =='en':
        await callback.message.edit_text(f"👋 Hello, <b>{callback.message.from_user.full_name}</b>! ⛅ My name is WeatherBot\n🤗 How can I help you?", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb), parse_mode='HTML')
    else:
        await callback.message.edit_text(f"👋 Привет, <b>{callback.message.from_user.full_name}</b>! ⛅ Меня зовут WeatherBot\n🤗 Как я могу помочь вам?", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb), parse_mode='HTML')


async def main() -> None:
    token = get_api()[1]
    bot = Bot(token)
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())
