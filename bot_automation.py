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

async def run_precise_purchase(target_hour):
    print(f"--- АКТИВИРОВАН ВЫСОКОТОЧНЫЙ ЦИКЛ ЗАКУПА (Цель: {target_hour}:00) ---")
    
    while True:
        now = datetime.now()
        
        # 1. УСЛОВИЕ ОСТАНОВКИ: Если время > 15:01:00 (для 15 часов)
        if now.hour == target_hour and now.minute >= 1 and now.second > 0:
            print("Время вышло, цикл остановлен.")
            break
            
        try:
            async with client.conversation(bot_username, timeout=3) as conv:
                # 2. Быстрый сброс и покупка
                await conv.send_message('/shop')
                resp = await conv.get_response()
                
                resp = await resp.click(data=b'get_product|119|1')
                
                resp = await conv.get_response()
                await resp.click(data=b'buy_product|119|')
                
                print(f"Успех в {now.strftime('%H:%M:%S')}!")
                return # Выходим при успехе
                
        except Exception:
            # Ошибки игнорируем, продолжаем долбить
            continue

async def main():
    await client.start()
    print("Бот-пулемет готов к запуску по таймингу.")
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    # Запуск за 20 секунд до часа (в 14:59:40)
    scheduler.add_job(run_precise_purchase, 'cron', hour=14, minute=59, second=40, args=[15])
    # Запуск за 20 секунд до 18:00 (в 17:59:40)
    scheduler.add_job(run_precise_purchase, 'cron', hour=17, minute=59, second=40, args=[18])
    
    scheduler.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
