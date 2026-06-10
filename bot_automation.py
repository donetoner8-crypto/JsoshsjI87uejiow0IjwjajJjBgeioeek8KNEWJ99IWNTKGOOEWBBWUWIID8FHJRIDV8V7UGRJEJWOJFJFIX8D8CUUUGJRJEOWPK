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

async def navigate_and_buy(conv):
    """Строгая логика: отправляет шоп, анализирует кнопки, жмет"""
    await conv.send_message('/shop')
    resp = await conv.get_response()
    
    if not resp.buttons:
        return "not_found"

    buttons_data = [b.data for row in resp.buttons for b in row]
    
    # 1. Если видим 119 -> ПОКУПАЕМ
    if b'get_product|119|1' in buttons_data:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Вижу 119 -> Покупаю!")
        await resp.click(data=b'get_product|119|1')
        resp = await conv.get_response()
        await resp.click(data=b'buy_product|119|')
        return "bought"

    # 2. Если видим 135 -> Жмем 3
    if b'get_product|135|1' in buttons_data:
        print("Вижу 135 (Стр 2) -> Жму 3")
        await resp.click(data=b'all_products|3')
        return "navigated"

    # 3. Если видим 151 -> Жмем 2
    if b'get_product|151|1' in buttons_data:
        print("Вижу 151 (Стр 1) -> Жму 2")
        await resp.click(data=b'all_products|2')
        return "navigated"
    
    return "not_found"

async def start_aggressive_mode(target_hour):
    """Агрессивный режим с удержанием одной сессии"""
    print(f"--- АГРЕССИВНЫЙ РЕЖИМ (Цель: {target_hour}:01) ---")
    
    # Открываем сессию ОДИН РАЗ
    async with client.conversation(bot_username, timeout=5) as conv:
        while True:
            now = datetime.now()
            if now.hour == target_hour and now.minute >= 1:
                print("Время вышло.")
                break
            
            try:
                status = await navigate_and_buy(conv)
                if status == "bought": 
                    break
                # Если "navigated" или "not_found", цикл сразу идет на новую итерацию
            except Exception:
                continue

async def test_full_cycle():
    """Проверка при старте"""
    print("--- ЗАПУСК ПРОВЕРОЧНОГО ЦИКЛА ---")
    try:
        async with client.conversation(bot_username, timeout=10) as conv:
            for _ in range(5): # Максимум 5 шагов для теста
                status = await navigate_and_buy(conv)
                if status == "bought" or status == "not_found": break
    except Exception as e:
        print(f"Ошибка теста: {e}")

async def main():
    await client.start()
    print("Бот запущен.")
    
    await test_full_cycle()
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(start_aggressive_mode, 'cron', hour=14, minute=59, second=40, args=[15])
    scheduler.add_job(start_aggressive_mode, 'cron', hour=17, minute=59, second=40, args=[18])
    
    scheduler.start()
    print("Ожидаю времени закупа...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
