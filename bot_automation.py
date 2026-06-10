import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Настройки
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
session_str = os.environ.get('SESSION_STRING')
bot_username = os.environ.get('BOT_USERNAME', 'happygalaxy_bot')

client = TelegramClient(StringSession(session_str), api_id, api_hash)

# 1. Функция подготовки (листает страницы за 2 минуты до закупа)
async def prepare_shop():
    print("--- Предварительная подготовка (листание страниц) ---")
    try:
        async with client.conversation(bot_username, timeout=45) as conv:
            await conv.send_message('/shop')
            resp = await conv.get_response()
            
            await resp.click(data=b'all_products|2')
            await asyncio.sleep(2.5)
            await resp.click(data=b'all_products|3')
            print("Страницы успешно пролистаны!")
    except Exception as e:
        print(f"Ошибка подготовки: {e}")

# 2. Функция покупки (в 15:00 и 18:00)
async def execute_purchase():
    print("--- Выполнение закупа ---")
    try:
        async with client.conversation(bot_username, timeout=45) as conv:
            await conv.send_message('/shop')
            resp1 = await conv.get_response()
            
            # Покупка товара
            await resp1.click(data=b'get_product|119|1')
            await asyncio.sleep(2.5)
            
            resp2 = await conv.get_response()
            await resp2.click(data=b'buy_product|119|')
            print("Закуп завершен!")
    except Exception as e:
        print(f"Ошибка закупа: {e}")

async def main():
    await client.start()
    print("Бот успешно авторизован!")
    
    # ПРОВЕРКА ПРИ СТАРТЕ: прогоняем полный цикл
    print("Выполняю тестовый прогон системы...")
    await prepare_shop()
    await execute_purchase()
    
    # Настройка планировщика
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    # Подготовка за 2 минуты (14:58 и 17:58)
    scheduler.add_job(prepare_shop, 'cron', hour=14, minute=58)
    scheduler.add_job(prepare_shop, 'cron', hour=17, minute=58)
    
    # Закуп ровно в 15:00:00 и 18:00:00
    scheduler.add_job(execute_purchase, 'cron', hour=15, minute=0, second=0)
    scheduler.add_job(execute_purchase, 'cron', hour=18, minute=0, second=0)
    
    scheduler.start()
    print("Планировщик запущен. Ожидаю расписания.")
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
