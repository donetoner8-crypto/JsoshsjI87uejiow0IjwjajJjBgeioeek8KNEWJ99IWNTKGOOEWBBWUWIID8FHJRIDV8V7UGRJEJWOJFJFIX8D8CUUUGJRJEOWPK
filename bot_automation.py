import os
import asyncio
import re
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- НАСТРОЙКИ ---
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
session_str = os.environ.get('SESSION_STRING')
bot_username = os.environ.get('BOT_USERNAME', 'happygalaxy_bot')

client = TelegramClient(StringSession(session_str), api_id, api_hash)
client.flood_sleep_threshold = 0

is_shooting = False

# --- ОБРАБОТЧИК ---
@client.on(events.NewMessage(from_users=bot_username))
async def handler(event):
    if not event.buttons:
        return
    
    text = event.raw_text
    buttons_data = [b.data for row in event.buttons for b in row]
    
    # 1. ФИЛЬТР: Если товар пуст, не ждем, а шлем /shop заново
    if "Общие Знания: 0📚" in text:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Пусто (0), рестарт /shop")
        await client.send_message(bot_username, '/shop')
        return

    # 2. ПОКУПКА (119)
    if b'get_product|119|1' in buttons_data:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ТОВАР 119 НАЙДЕН! ПОКУПАЮ!")
        await event.click(data=b'get_product|119|1')
        await asyncio.sleep(0.05)
        await client.send_message(bot_username, 'buy_product|119|')
        return

    # 3. НАВИГАЦИЯ
    if b'get_product|135|1' in buttons_data:
        await event.click(data=b'all_products|3')
    elif b'get_product|151|1' in buttons_data:
        await event.click(data=b'all_products|2')

# --- ЗАДАЧИ ---
async def navigate_to_page_3():
    print("--- ПОДГОТОВКА: Иду на 3 страницу ---")
    for _ in range(5):
        await client.send_message(bot_username, '/shop')
        await asyncio.sleep(0.6)

async def start_shooting(target_hour):
    global is_shooting
    is_shooting = True
    print(f"--- ПУЛЕМЕТ ЗАПУЩЕН (Цель: {target_hour}:01) ---")
    while is_shooting:
        if datetime.now().hour == target_hour and datetime.now().minute >= 1:
            is_shooting = False
            break
        await client.send_message(bot_username, '/shop')
        await asyncio.sleep(0.3)

async def main():
    await client.start()
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    # Подготовка за 2 минуты
    scheduler.add_job(navigate_to_page_3, 'cron', hour=14, minute=58)
    scheduler.add_job(navigate_to_page_3, 'cron', hour=17, minute=58)
    
    # Режим охоты
    scheduler.add_job(start_shooting, 'cron', hour=15, minute=0, args=[15])
    scheduler.add_job(start_shooting, 'cron', hour=18, minute=0, args=[18])
    
    scheduler.start()
    print("Бот готов. Все системы активны.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
