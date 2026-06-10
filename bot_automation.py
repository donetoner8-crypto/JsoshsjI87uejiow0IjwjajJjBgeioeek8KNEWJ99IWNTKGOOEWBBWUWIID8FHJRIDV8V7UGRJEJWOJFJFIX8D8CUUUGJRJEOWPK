import os
import asyncio
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

# Флаг состояния
is_running = False

@client.on(events.NewMessage(from_users=bot_username))
async def handler(event):
    if not event.buttons:
        return
    
    buttons_data = [b.data for row in event.buttons for b in row]
    
    # 1. СРАЗУ К ПОКУПКЕ (если видим товар 119)
    if b'get_product|119|1' in buttons_data:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ПРЯМОЙ ПЕРЕХОД К ПОКУПКЕ!")
        # Кликаем выбор товара
        await event.click(data=b'get_product|119|1')
        # Ждем микросекунды и шлем подтверждение покупки
        await asyncio.sleep(0.05)
        await client.send_message(bot_username, 'buy_product|119|')
        return

    # 2. Навигация
    if b'get_product|135|1' in buttons_data:
        await event.click(data=b'all_products|3')
    elif b'get_product|151|1' in buttons_data:
        await event.click(data=b'all_products|2')

async def start_shooting(target_hour):
    global is_running
    is_running = True
    print(f"--- ПУЛЕМЕТ ЗАПУЩЕН (Цель: {target_hour}:01) ---")
    
    while is_running:
        now = datetime.now()
        if now.hour == target_hour and now.minute >= 1:
            is_running = False
            break
            
        await client.send_message(bot_username, '/shop')
        await asyncio.sleep(0.2) # Сверхбыстрый пулемет

async def main():
    await client.start()
    
    # АВТО-ПЕРЕХОД ПРИ ЗАПУСКЕ
    print("Автоматический проход к покупке при старте...")
    await client.send_message(bot_username, '/shop')
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(start_shooting, 'cron', hour=14, minute=59, second=40, args=[15])
    scheduler.add_job(start_shooting, 'cron', hour=17, minute=59, second=40, args=[18])
    
    scheduler.start()
    print("Ожидаю времени закупа...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
