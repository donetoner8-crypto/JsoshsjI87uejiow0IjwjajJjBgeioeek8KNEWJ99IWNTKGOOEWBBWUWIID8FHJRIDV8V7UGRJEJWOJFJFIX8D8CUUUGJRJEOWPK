import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

# Настройки
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
session_str = os.environ.get('SESSION_STRING')
bot_username = os.environ.get('BOT_USERNAME', 'happygalaxy_bot')

client = TelegramClient(StringSession(session_str), api_id, api_hash)

# Флаг, чтобы настройки страниц выполнялись только 1 раз в сутки
daily_setup_done = False

async def setup_pages():
    global daily_setup_done
    print("--- Настройка страниц (листаем кнопки) ---")
    try:
        async with client.conversation(bot_username, timeout=30) as conv:
            await conv.send_message('/shop')
            resp = await conv.get_response()
            
            # Нажимаем кнопки для пролистывания страниц
            await resp.click(data=b'all_products|2')
            await asyncio.sleep(1)
            await resp.click(data=b'all_products|3')
            await asyncio.sleep(1)
            await resp.click(data=b'all_products|4')
            
            daily_setup_done = True
            print("Страницы настроены!")
    except Exception as e:
        print(f"Ошибка при настройке: {e}")

async def make_purchase():
    print("--- Покупка товара ---")
    try:
        async with client.conversation(bot_username, timeout=30) as conv:
            # Если еще не нажимали кнопки сегодня, делаем это
            if not daily_setup_done:
                await setup_pages()
            
            # Сама покупка
            await conv.send_message('/shop')
            resp = await conv.get_response()
            await resp.click(data=b'get_product|119|1')
            await asyncio.sleep(2)
            resp2 = await conv.get_response()
            await resp2.click(data=b'buy_product|119|')
            print("Покупка совершена!")
    except Exception as e:
        print(f"Ошибка покупки: {e}")

async def reset_daily_flag():
    global daily_setup_done
    daily_setup_done = False
    print("Флаг настроек сброшен для нового дня.")

async def main():
    await client.start()
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    # 1. Настройка страниц в 14:58 (за 2 минуты до 15:00)
    scheduler.add_job(setup_pages, 'cron', hour=14, minute=58)
    
    # 2. Покупки в 15:00 и 18:00
    scheduler.add_job(make_purchase, 'cron', hour=15, minute=0)
    scheduler.add_job(make_purchase, 'cron', hour=18, minute=0)
    
    # 3. Сброс флага настроек в полночь, чтобы завтра всё повторилось
    scheduler.add_job(reset_daily_flag, 'cron', hour=0, minute=0)
    
    scheduler.start()
    print("Бот запущен и ждет расписания.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
