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

# Функция цикла закупа (универсальная)
async def run_purchase_loop():
    print(f"--- ЗАПУСК ЦИКЛА ЗАКУПА {datetime.now().strftime('%H:%M:%S')} ---")
    
    # 1. Сначала делаем одну попытку (это и есть тот самый "1 цикл")
    try:
        async with client.conversation(bot_username, timeout=5) as conv:
            await conv.send_message('/shop')
            resp = await conv.get_response()
            
            # Клик по товару
            resp = await resp.click(data=b'get_product|119|1')
            
            # Подтверждение
            resp = await conv.get_response()
            await resp.click(data=b'buy_product|119|')
            
            print("Успех: Товар куплен!")
            return True # Успех
    except Exception as e:
        print(f"Проход завершен (ошибка или нет товара): {e}")
        return False

# Функция для "пулемета" (до 15:01)
async def start_aggressive_mode(target_hour):
    print(f"--- РЕЖИМ ПУЛЕМЕТА ВКЛЮЧЕН (до {target_hour}:01) ---")
    while True:
        now = datetime.now()
        # Выход, если минута >= 1
        if now.hour == target_hour and now.minute >= 1:
            print("Время вышло.")
            break
        
        success = await run_purchase_loop()
        if success: break # Если купили — прекращаем долбить

async def main():
    await client.start()
    print("Бот запущен.")
    
    # --- ПРОВЕРОЧНЫЙ ЦИКЛ ПРИ СТАРТЕ ---
    print("Выполняю обязательный цикл проверки при включении...")
    await run_purchase_loop()
    print("Проверка завершена. Перехожу в режим ожидания.")
    # -----------------------------------
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    # Запуск за 20 секунд до часа
    scheduler.add_job(start_aggressive_mode, 'cron', hour=14, minute=59, second=40, args=[15])
    scheduler.add_job(start_aggressive_mode, 'cron', hour=17, minute=59, second=40, args=[18])
    
    scheduler.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
