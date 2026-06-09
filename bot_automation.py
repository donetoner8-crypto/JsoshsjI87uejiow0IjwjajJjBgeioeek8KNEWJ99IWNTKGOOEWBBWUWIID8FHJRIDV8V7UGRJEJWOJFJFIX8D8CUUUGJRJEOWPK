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

async def shop_routine():
    print("--- Запуск цикла (подготовка + покупка) ---")
    try:
        async with client.conversation(bot_username, timeout=30) as conv:
            # 1. Заходим в шоп
            await conv.send_message('/shop')
            resp = await conv.get_response()
            
            # 2. Пытаемся прокликать страницы (игнорируем ошибки, если кнопок нет)
            try:
                await resp.click(data=b'all_products|2')
                await asyncio.sleep(1)
                await resp.click(data=b'all_products|3')
                await asyncio.sleep(1)
                await resp.click(data=b'all_products|4')
                await asyncio.sleep(1)
            except Exception:
                pass # Если кнопок нет, просто идем дальше
            
            # 3. Сама покупка
            await resp.click(data=b'get_product|119|1')
            await asyncio.sleep(2)
            
            resp2 = await conv.get_response()
            await resp2.click(data=b'buy_product|119|')
            
            print("Цикл завершен!")
    except Exception as e:
        print(f"Критическая ошибка: {e}")

async def main():
    await client.start()
    
    # Сразу прогоним один раз для проверки
    await shop_routine()
    
    # Планировщик на 15:00 и 18:00
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(shop_routine, 'cron', hour=15, minute=0)
    scheduler.add_job(shop_routine, 'cron', hour=18, minute=0)
    
    scheduler.start()
    print("Бот готов к работе.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
