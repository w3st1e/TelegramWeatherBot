import aiosqlite
import asyncio

async def add_to_db(user_id, balance=0, lang='en'):
    connect = await aiosqlite.connect('D:/pythoncodes/TelegramBotWeather/usersdb')
    cursor = await connect.cursor()
    await cursor.execute('SELECT * FROM users WHERE userid = ?', (user_id,))
    if not await cursor.fetchone():
        await cursor.execute('INSERT INTO users VALUES (?, ?, ?)', (user_id, balance, lang))
        await connect.commit()
    await cursor.close()
    await connect.close()