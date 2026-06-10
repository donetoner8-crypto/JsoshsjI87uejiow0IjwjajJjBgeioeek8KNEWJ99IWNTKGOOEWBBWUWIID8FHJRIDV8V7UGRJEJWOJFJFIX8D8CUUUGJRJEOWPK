import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Загружаем настройки из переменных окружения
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
session_str = os.environ.get('SESSION_STRING')
bot_username = os.environ.get('BOT_USERNAME', 'happygalaxy_bot')

client = TelegramClient(StringSession(session_str), api_id, api_hash)

# 1. Функция подготовки (листаем за 2 минуты до закупа)
async def prepare_shop():
    print("--- Предварительная подготовка страниц ---")
    try:
        async with client.conversation(bot_username, timeout=20) as conv:
            await conv.send_message('/shop')
            resp = await conv.get_response()
            # Кнопки листания
            await resp.click(data=b'all_products|2')
            await asyncio.sleep(1.0)
            await resp.click(data=b'all_products|3')
            print("Страницы успешно пролистаны!")
    except Exception as e:
        print(f"Ошибка подготовки: {e}")

# 2. Функция покупки (в 15:00:00 и 18:00:00)
async def execute_purchase():
    print("--- Выполнение закупа ---")
    try:
        async with client.conversation(bot_username, timeout=20) as conv:
            await conv.send_message('/shop')
            resp = await conv.get_response()
            # Покупка
            await resp.click(data=b'get_product|119|1')
            await asyncio.sleep(0.5)
            resp2 = await conv.get_response()
            await resp2.click(data=b'buy_product|119|')
            print("Закуп завершен успешно!")
    except Exception as e:
        print(f"Ошибка закупа: {e}")

async def main():
    await client.start()
    print("Бот успешно авторизован!")
    
    # ПРОВЕРКА ПРИ СТАРТЕ: прогон системы
    print("Выполняю тестовый прогон системы...")
    await prepare_shop()
    await execute_purchase()
    
    # Настройка планировщика
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    # Подготовка за 2 минуты
    scheduler.add_job(prepare_shop, 'cron', hour=14, minute=58)
    scheduler.add_job(prepare_shop, 'cron', hour=17, minute=58)
    
    # Закуп ровно в 15:00 и 18:00
    scheduler.add_job(execute_purchase, 'cron', hour=15, minute=0, second=0)
    scheduler.add_job(execute_purchase, 'cron', hour=18, minute=0, second=0)
    
    scheduler.start()
    print("Планировщик запущен. Ожидаю расписания.")
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
