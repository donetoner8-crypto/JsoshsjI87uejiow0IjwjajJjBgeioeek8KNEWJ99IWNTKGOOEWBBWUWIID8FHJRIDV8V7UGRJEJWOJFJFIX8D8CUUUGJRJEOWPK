import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- НАСТРОЙКИ ---
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
session_str = os.environ.get('SESSION_STRING')
bot_username = os.environ.get('BOT_USERNAME', 'happygalaxy_bot')

client = TelegramClient(StringSession(session_str), api_id, api_hash)

# Функция для «быстрого» перехода через сброс /shop
async def fast_navigate(conv, data_string):
    """Сбрасывает контекст через /shop и кликает"""
    await conv.send_message('/shop')
    resp = await conv.get_response()
    # Мгновенный клик
    await resp.click(data=data_string)
    print(f"Сброс и переход: {data_string.decode('utf-8')}")

# Основная функция закупа
async def run_purchase_flow():
    print("--- ЗАПУСК ЦИКЛА ЗАКУПА ---")
    try:
        async with client.conversation(bot_username, timeout=45) as conv:
            # 1. Быстрый переход по страницам (без КД)
            await fast_navigate(conv, b'all_products|2')
            await fast_navigate(conv, b'all_products|3')
            
            # 2. Финальный заход за товаром
            await conv.send_message('/shop')
            resp = await conv.get_response()
            
            # Если видим кнопку товара - покупаем
            # Используем click без await asyncio.sleep для скорости, 
            # кроме финального подтверждения
            resp = await resp.click(data=b'get_product|119|1')
            
            # 3. Финальное подтверждение с небольшой паузой для сервера
            resp = await conv.get_response()
            await resp.click(data=b'buy_product|119|')
            
            print("Успех: Товар куплен!")
            
    except Exception as e:
        print(f"Ошибка в процессе: {e}")

async def main():
    await client.start()
    print("Бот запущен и авторизован.")
    
    # Первичная проверка при старте
    await run_purchase_flow()
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    # Расписание (за 2 минуты до закупа и в ровное время)
    # Если бот уже купил в 14:58/17:58, он просто снова пролистает меню в 15:00/18:00
    scheduler.add_job(run_purchase_flow, 'cron', hour=14, minute=58)
    scheduler.add_job(run_purchase_flow, 'cron', hour=15, minute=0)
    scheduler.add_job(run_purchase_flow, 'cron', hour=17, minute=58)
    scheduler.add_job(run_purchase_flow, 'cron', hour=18, minute=0)
    
    scheduler.start()
    print("Планировщик активен.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
