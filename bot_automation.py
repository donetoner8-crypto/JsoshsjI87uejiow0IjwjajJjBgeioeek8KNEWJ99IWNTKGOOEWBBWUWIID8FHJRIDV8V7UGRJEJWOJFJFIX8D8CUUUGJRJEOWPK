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

# Флаг для остановки
is_running = False

async def aggressive_shooter(target_hour):
    global is_running
    is_running = True
    print(f"--- АГРЕССИВНЫЙ РЕЖИМ (до {target_hour}:01) ---")
    
    while is_running:
        now = datetime.now()
        if now.hour == target_hour and now.minute >= 1:
            is_running = False
            break
            
        # Пулеметим команду
        await client.send_message(bot_username, '/shop')
        # Ждем всего 0.5 сек перед следующим выстрелом
        await asyncio.sleep(0.5)

@client.on(events.NewMessage(from_users=bot_username))
async def handler(event):
    if not is_running:
        return

    # Если в сообщении есть кнопки, анализируем их
    if event.buttons:
        # Собираем данные всех кнопок
        buttons_data = [b.data for row in event.buttons for b in row]
        
        # 1. Покупка (Цель 119)
        if b'get_product|119|1' in buttons_data:
            print("Вижу 119 -> Покупаю!")
            await event.click(data=b'get_product|119|1')
            await asyncio.sleep(0.1)
            await client.send_message(bot_username, 'buy_product|119|')
            return

        # 2. Переход (Цель 135 -> 3)
        if b'get_product|135|1' in buttons_data:
            await event.click(data=b'all_products|3')
            return

        # 3. Переход (Цель 151 -> 2)
        if b'get_product|151|1' in buttons_data:
            await event.click(data=b'all_products|2')
            return

async def main():
    await client.start()
    print("Бот готов к пулеметной стрельбе.")
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(aggressive_shooter, 'cron', hour=14, minute=59, second=40, args=[15])
    scheduler.add_job(aggressive_shooter, 'cron', hour=17, minute=59, second=40, args=[18])
    
    scheduler.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
