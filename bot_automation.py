import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
session_str = os.environ.get('SESSION_STRING')
bot_username = os.environ.get('BOT_USERNAME', 'happygalaxy_bot')

client = TelegramClient(StringSession(session_str), api_id, api_hash)

# Функция для нажатия кнопки и получения ответа
async def click_button(message, data_string, delay=3.0):
    print(f"Нажимаю кнопку: {data_string.decode('utf-8')}")
    new_message = await message.click(data=data_string)
    await asyncio.sleep(delay)
    return new_message

# Функция поиска кнопок в сообщении
def has_button(message, data_string):
    for row in message.buttons:
        for button in row:
            if button.data == data_string:
                return True
    return False

# Основная логика выбора
async def decide_and_act(conv, message):
    data = [b.data for row in message.buttons for b in row]
    
    # 1. Если есть all_products|3 и all_products|4 -> ПОКУПАЕМ
    if b'all_products|3' in data and b'all_products|4' in data:
        print("Найдена пара 3 и 4: Перехожу к покупке!")
        msg = await click_button(message, b'get_product|119|1')
        msg = await conv.get_response()
        await click_button(msg, b'buy_product|119|')
        return True # Покупка совершена
    
    # 2. Если есть кнопки 1 и 3 -> жмем 3
    elif b'all_products|1' in data and b'all_products|3' in data:
        print("Найдена пара 1 и 3: Перехожу на 3...")
        new_msg = await click_button(message, b'all_products|3')
        return await decide_and_act(conv, new_msg) # Рекурсивно проверяем новую страницу
        
    # 3. Если есть только 2 -> жмем 2
    elif b'all_products|2' in data:
        print("Найдена 2: Перехожу на 2...")
        new_msg = await click_button(message, b'all_products|2')
        return await decide_and_act(conv, new_msg)
    
    print("Условия не соблюдены, жду...")
    return False

async def run_process():
    try:
        async with client.conversation(bot_username, timeout=45) as conv:
            await conv.send_message('/shop')
            resp = await conv.get_response()
            await decide_and_act(conv, resp)
    except Exception as e:
        print(f"Ошибка процесса: {e}")

async def main():
    await client.start()
    
    # Авто-проверка при старте
    await run_process()
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    # Запуск за 2 минуты (подготовка) и в нужное время
    scheduler.add_job(run_process, 'cron', hour=14, minute=58)
    scheduler.add_job(run_process, 'cron', hour=15, minute=0)
    scheduler.add_job(run_process, 'cron', hour=17, minute=58)
    scheduler.add_job(run_process, 'cron', hour=18, minute=0)
    
    scheduler.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
