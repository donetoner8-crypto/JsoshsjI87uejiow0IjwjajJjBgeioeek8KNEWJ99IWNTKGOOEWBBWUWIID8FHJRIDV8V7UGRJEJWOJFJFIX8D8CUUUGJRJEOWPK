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

async def attempt_purchase():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Попытка закупа...")
    try:
        async with client.conversation(bot_username, timeout=10) as conv:
            await conv.send_message('/shop')
            resp = await conv.get_response()
            
            # --- ДИАГНОСТИКА ---
            if resp.buttons:
                print("Найдены кнопки:")
                for row in resp.buttons:
                    for btn in row:
                        print(f"  > Текст: {btn.text} | Data: {btn.data}")
            else:
                print("!!! В сообщении НЕТ кнопок (или бот прислал текст без них)")
                return False
            # --------------------

            # Попытка клика
            target_data = b'get_product|119|1'
            
            # Ищем кнопку в данных
            found_btn = None
            for row in resp.buttons:
                for btn in row:
                    if btn.data == target_data:
                        found_btn = btn
            
            if found_btn:
                await found_btn.click()
                print("Кнопка товара нажата!")
                
                # Подтверждение
                resp2 = await conv.get_response()
                # Ищем кнопку buy_product
                for row in resp2.buttons:
                    for btn in row:
                        if b'buy_product' in btn.data:
                            await btn.click()
                            print("!!! УСПЕХ: Покупка подтверждена !!!")
                            return True
            else:
                print("Кнопка товара не найдена в текущем меню.")
                
    except Exception as e:
        print(f"Ошибка в цикле: {e}")
    return False

async def aggressive_mode(target_hour):
    print(f"--- АГРЕССИВНЫЙ РЕЖИМ (до {target_hour}:01) ---")
    while True:
        now = datetime.now()
        if now.hour == target_hour and now.minute >= 1:
            break
        
        success = await attempt_purchase()
        if success: break
        await asyncio.sleep(0.5) # Минимальная пауза между циклами, чтобы не спамить в Телеграм

async def main():
    await client.start()
    print("Бот запущен. Тестовый цикл...")
    await attempt_purchase()
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(aggressive_mode, 'cron', hour=14, minute=59, second=40, args=[15])
    scheduler.add_job(aggressive_mode, 'cron', hour=17, minute=59, second=40, args=[18])
    
    scheduler.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
