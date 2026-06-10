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

# Флаг для пулемета
is_shooting = False

@client.on(events.NewMessage(from_users=bot_username))
async def handler(event):
    # Если кнопок нет, ничего не делаем
    if not event.buttons:
        return
    
    buttons_data = [b.data for row in event.buttons for b in row]
    
    # 1. Покупка (119) - ПРИОРИТЕТ
    if b'get_product|119|1' in buttons_data:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] НАШЕЛ 119 - ПОКУПАЮ!")
        await event.click(data=b'get_product|119|1')
        await asyncio.sleep(0.1)
        await client.send_message(bot_username, 'buy_product|119|')
        return

    # 2. Навигация со страницы 2 (135 -> 3)
    if b'get_product|135|1' in buttons_data:
        print("На странице 2, жму 3")
        await event.click(data=b'all_products|3')
        return

    # 3. Навигация со страницы 1 (151 -> 2)
    if b'get_product|151|1' in buttons_data:
        print("На странице 1, жму 2")
        await event.click(data=b'all_products|2')
        return

async def start_shooting(target_hour):
    global is_shooting
    is_shooting = True
    print(f"--- ПУЛЕМЕТ РАБОТАЕТ (до {target_hour}:01) ---")
    
    while is_shooting:
        now = datetime.now()
        if now.hour == target_hour and now.minute >= 1:
            is_shooting = False
            break
        
        await client.send_message(bot_username, '/shop')
        await asyncio.sleep(0.3) 

async def main():
    await client.start()
    
    # --- ДОХОДИМ ДО ПОКУПКИ ПРИ ЗАПУСКЕ ---
    print("Пробую дойти до покупки при запуске...")
    await client.send_message(bot_username, '/shop')
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(start_shooting, 'cron', hour=14, minute=59, second=40, args=[15])
    scheduler.add_job(start_shooting, 'cron', hour=17, minute=59, second=40, args=[18])
    
    scheduler.start()
    print("Бот готов. Ожидаю времени закупа...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
