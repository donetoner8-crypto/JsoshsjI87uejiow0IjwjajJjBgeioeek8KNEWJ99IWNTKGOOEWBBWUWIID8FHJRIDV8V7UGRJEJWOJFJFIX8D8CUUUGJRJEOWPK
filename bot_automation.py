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

async def manual_click(message, data_string):
    """Нажимает кнопку и ждет заданное время"""
    print(f"Нажимаю кнопку: {data_string.decode('utf-8')}")
    await message.click(data=data_string)
    await asyncio.sleep(1.5) # Твоя задержка для стабильности

async def prepare_shop():
    print("--- Подготовка: листание страниц ---")
    try:
        async with client.conversation(bot_username, timeout=30) as conv:
            msg = await conv.send_message('/shop')
            resp = await conv.get_response()
            
            await manual_click(resp, b'all_products|2')
            # resp обновляется автоматически после получения нового сообщения от бота
            resp = await conv.get_response() 
            await manual_click(resp, b'all_products|3')
            print("Страницы пролистаны.")
    except Exception as e:
        print(f"Ошибка подготовки: {e}")

async def execute_purchase():
    print("--- Выполнение закупа ---")
    try:
        async with client.conversation(bot_username, timeout=30) as conv:
            await conv.send_message('/shop')
            resp = await conv.get_response()
            
            # Покупка товара
            await manual_click(resp, b'get_product|119|1')
            
            # Ждем подтверждения
            resp = await conv.get_response()
            await manual_click(resp, b'buy_product|119|')
            
            print("Закуп успешно завершен!")
    except Exception as e:
        print(f"Ошибка закупа: {e}")

async def main():
    await client.start()
    print("Бот успешно запущен.")
    
    # Проверка при старте
    await prepare_shop()
    await execute_purchase()
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    # Листание за 2 минуты до закупа
    scheduler.add_job(prepare_shop, 'cron', hour=14, minute=58)
    scheduler.add_job(prepare_shop, 'cron', hour=17, minute=58)
    
    # Закуп ровно в 15:00 и 18:00
    scheduler.add_job(execute_purchase, 'cron', hour=15, minute=0, second=0)
    scheduler.add_job(execute_purchase, 'cron', hour=18, minute=0, second=0)
    
    scheduler.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
