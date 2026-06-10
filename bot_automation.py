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

# 1. Функция подготовки
async def prepare_shop():
    print("--- Подготовка: листаем страницы ---")
    try:
        async with client.conversation(bot_username, timeout=30) as conv:
            msg = await conv.send_message('/shop')
            resp = await conv.get_response()
            
            # Обновляем resp после каждого клика
            resp = await resp.click(data=b'all_products|2')
            resp = await resp.click(data=b'all_products|3')
            print("Страницы успешно пролистаны.")
    except Exception as e:
        print(f"Ошибка подготовки: {e}")

# 2. Функция покупки
async def execute_purchase():
    print("--- Выполнение закупа ---")
    try:
        async with client.conversation(bot_username, timeout=30) as conv:
            msg = await conv.send_message('/shop')
            resp = await conv.get_response()
            
            # Покупка: клик -> получение ответа -> клик
            resp = await resp.click(data=b'get_product|119|1')
            
            # Ждем подтверждения, если бот его присылает
            resp = await conv.get_response() 
            await resp.click(data=b'buy_product|119|')
            
            print("Закуп завершен успешно!")
    except Exception as e:
        print(f"Ошибка закупа: {e}")

async def main():
    await client.start()
    print("Бот авторизован.")
    
    # Тестовый прогон при старте
    await prepare_shop()
    await execute_purchase()
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    # Расписание
    scheduler.add_job(prepare_shop, 'cron', hour=14, minute=58)
    scheduler.add_job(prepare_shop, 'cron', hour=17, minute=58)
    scheduler.add_job(execute_purchase, 'cron', hour=15, minute=0, second=0)
    scheduler.add_job(execute_purchase, 'cron', hour=18, minute=0, second=0)
    
    scheduler.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
