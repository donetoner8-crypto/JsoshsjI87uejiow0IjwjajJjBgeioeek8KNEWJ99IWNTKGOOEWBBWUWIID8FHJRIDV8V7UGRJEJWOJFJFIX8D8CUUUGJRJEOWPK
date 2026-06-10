import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Настройки
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
session_str = os.environ.get('SESSION_STRING')
bot_username = os.environ.get('BOT_USERNAME', 'happygalaxy_bot')

client = TelegramClient(StringSession(session_str), api_id, api_hash)

# Универсальная функция нажатия с задержкой 3 секунды
async def click_if_exists(message, data_string, delay=3.0):
    for row in message.buttons:
        for button in row:
            if button.data == data_string:
                print(f"Найдена: {data_string.decode('utf-8')}. Нажимаю...")
                new_message = await message.click(data=data_string)
                # Задержка 3 секунды после каждого клика
                await asyncio.sleep(delay)
                return new_message
    print(f"Кнопка {data_string.decode('utf-8')} не найдена.")
    return message

# 1. Функция листания (за 2 минуты до закупа)
async def prepare_shop():
    print("--- Предварительное листание ---")
    try:
        async with client.conversation(bot_username, timeout=45) as conv:
            await conv.send_message('/shop')
            resp = await conv.get_response()
            # Проходим по цепочке страниц
            resp = await click_if_exists(resp, b'all_products|2')
            resp = await click_if_exists(resp, b'all_products|3')
            resp = await click_if_exists(resp, b'all_products|4')
            print("Страницы успешно пролистаны.")
    except Exception as e:
        print(f"Ошибка листания: {e}")

# 2. Функция закупа (ровно в 15:00 и 18:00)
async def execute_purchase():
    print("--- Выполнение закупа ---")
    try:
        async with client.conversation(bot_username, timeout=45) as conv:
            await conv.send_message('/shop')
            resp = await conv.get_response()
            
            # Покупаем
            resp = await click_if_exists(resp, b'get_product|119|1')
            resp = await conv.get_response()
            await click_if_exists(resp, b'buy_product|119|')
            print("Закуп завершен!")
    except Exception as e:
        print(f"Ошибка закупа: {e}")

async def main():
    await client.start()
    print("Бот в режиме ожидания расписания.")
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    # Расписание листания
    scheduler.add_job(prepare_shop, 'cron', hour=14, minute=58)
    scheduler.add_job(prepare_shop, 'cron', hour=17, minute=58)
    
    # Расписание покупок
    scheduler.add_job(execute_purchase, 'cron', hour=15, minute=0, second=0)
    scheduler.add_job(execute_purchase, 'cron', hour=18, minute=0, second=0)
    
    scheduler.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
