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
    """Строгая логика навигации и покупки"""
    await conv.send_message('/shop')
    resp = await conv.get_response()
    
    if not resp.buttons:
        print("Кнопок в ответе нет.")
        return False

    buttons_data = [b.data for row in resp.buttons for b in row]

    # 1. Проверка: есть ли 3 и 4 (Покупка)
    if b'all_products|3' in buttons_data and b'all_products|4' in buttons_data:
        print("Найдена пара 3 и 4 -> Покупка!")
        resp = await resp.click(data=b'get_product|119|1')
        resp = await conv.get_response()
        await resp.click(data=b'buy_product|119|')
        return True 

    # 2. Проверка: есть ли 2 и 3 (Навигация)
    if b'all_products|2' in buttons_data and b'all_products|3' in buttons_data:
        print("Найдена пара 2 и 3 -> Жму 3")
        await resp.click(data=b'all_products|3')
        return False

    # 3. Проверка: есть ли только 2 (Навигация)
    if b'all_products|2' in buttons_data:
        print("Найдена 2 -> Жму 2")
        await resp.click(data=b'all_products|2')
        return False
    
    return False

async def start_aggressive_mode(target_hour):
    print(f"--- АГРЕССИВНЫЙ РЕЖИМ (Цель: {target_hour}:01) ---")
    while True:
        now = datetime.now()
        
        # Стоп-кран в 01 минуту
        if now.hour == target_hour and now.minute >= 1:
            print("Время вышло. Остановка цикла.")
            break
        
        try:
            async with client.conversation(bot_username, timeout=3) as conv:
                success = await navigate_and_buy(conv)
                if success: 
                    print("Товар успешно куплен!")
                    break
        except Exception:
            # Ошибки связи игнорим, сразу летим на новый цикл с /shop
            continue
        
        # Минимальная задержка перед следующим циклом
        await asyncio.sleep(0.1)

async def main():
    await client.start()
    print("Бот готов к работе.")
    
    # --- ПРОВЕРКА ПРИ ЗАПУСКЕ ---
    print("Выполняю 1 тестовый цикл при старте...")
    try:
        async with client.conversation(bot_username, timeout=5) as conv:
            await navigate_and_buy(conv)
            print("Тестовый цикл завершен успешно. Бот видит магазин.")
    except Exception as e:
        print(f"Ошибка при тестовом запуске: {e}")
    # -----------------------------
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    # Расписание запуска
    scheduler.add_job(start_aggressive_mode, 'cron', hour=14, minute=59, second=40, args=[15])
    scheduler.add_job(start_aggressive_mode, 'cron', hour=17, minute=59, second=40, args=[18])
    
    scheduler.start()
    print("Расписание активно. Ожидаю времени закупа...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
