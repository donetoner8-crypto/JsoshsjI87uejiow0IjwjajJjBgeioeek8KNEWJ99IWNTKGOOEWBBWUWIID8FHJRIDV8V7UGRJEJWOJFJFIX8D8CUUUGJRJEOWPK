import os
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- НАСТРОЙКИ ---
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
session_str = os.environ.get('SESSION_STRING')
bot_username = os.environ.get('BOT_USERNAME', 'happygalaxy_bot')

client = TelegramClient(StringSession(session_str), api_id, api_hash)

# Функция проверки работоспособности (при старте)
async def startup_check():
    print("--- ЗАПУСК ПРОВЕРКИ СВЯЗИ ---")
    try:
        async with client.conversation(bot_username, timeout=10) as conv:
            await conv.send_message('/shop')
            resp = await conv.get_response()
            if resp:
                print(f"Связь есть! Ответ бота: {resp.text[:30]}...")
    except Exception as e:
        print(f"!!! ОШИБКА СВЯЗИ ПРИ СТАРТЕ: {e}")

# Высокоточный цикл закупа
async def run_precise_purchase(target_hour):
    print(f"--- АКТИВИРОВАН ЦИКЛ (Цель: {target_hour}:00) ---")
    while True:
        now = datetime.now()
        # Стоп: если уже 01 минута часа (кроме случая target_hour)
        if now.hour == target_hour and now.minute >= 1:
            print("Время вышло, завершаю цикл.")
            break
            
        try:
            async with client.conversation(bot_username, timeout=3) as conv:
                await conv.send_message('/shop')
                resp = await conv.get_response()
                
                resp = await resp.click(data=b'get_product|119|1')
                resp = await conv.get_response()
                await resp.click(data=b'buy_product|119|')
                
                print(f"Успех в {now.strftime('%H:%M:%S')}!")
                return 
        except Exception:
            continue

async def main():
    await client.start()
    print("Бот авторизован.")
    
    # ПРОВЕРКА ПРИ ВКЛЮЧЕНИИ
    await startup_check()
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    # Расписание
    scheduler.add_job(run_precise_purchase, 'cron', hour=14, minute=59, second=40, args=[15])
    scheduler.add_job(run_precise_purchase, 'cron', hour=17, minute=59, second=40, args=[18])
    
    scheduler.start()
    print("Планировщик запущен, жду времени...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
