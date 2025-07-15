import aiosqlite
import asyncio

async def add_to_db(user_id, balance=0, lang='en'):
    connect = await aiosqlite.connect('D:/pythoncodes/TelegramBotWeather/weathertg.db')
    cursor = await connect.cursor()
    await cursor.execute('SELECT * FROM users WHERE userid = ?', (user_id,))
    if not await cursor.fetchone():
        await cursor.execute('INSERT INTO users VALUES (?, ?, ?)', (user_id, balance, lang))
        await connect.commit()
    await cursor.close()
    await connect.close()


async def get_balance(user_id):
    connect = await aiosqlite.connect('D:/pythoncodes/TelegramBotWeather/weathertg.db')
    cursor = await connect.cursor()
    await cursor.execute('SELECT balance FROM users WHERE userid = ?', (user_id,))
    balance = await cursor.fetchone()
    await cursor.close()
    await connect.close()
    return balance[0] if balance else 0

async def get_lang(user_id):
    connect = await aiosqlite.connect('D:/pythoncodes/TelegramBotWeather/weathertg.db')
    cursor = await connect.cursor()
    await cursor.execute('SELECT lang FROM users WHERE userid = ?', (user_id,))
    lang = await cursor.fetchone()
    await cursor.close()
    await connect.close()
    return lang[0] if lang else 'en'

async def set_lang(user_id, language) -> None:
    connect = await aiosqlite.connect('D:/pythoncodes/TelegramBotWeather/weathertg.db')
    cursor = await connect.cursor()
    await cursor.execute('UPDATE users SET lang = ? WHERE userid = ?', (language, user_id))
    await connect.commit()
    await cursor.close()
    await connect.close()

async def change_balance(user_id, calls) -> None:
    connect = await aiosqlite.connect('D:/pythoncodes/TelegramBotWeather/weathertg.db')
    cursor = await connect.cursor()
    await cursor.execute('UPDATE users SET balance = ? WHERE userid = ?', (calls, user_id))
    await connect.commit()
    await cursor.close()
    await connect.close()


