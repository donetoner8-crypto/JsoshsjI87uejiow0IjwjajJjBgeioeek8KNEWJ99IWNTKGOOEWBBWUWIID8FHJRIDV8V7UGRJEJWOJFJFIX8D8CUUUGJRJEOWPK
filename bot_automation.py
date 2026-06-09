import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Загружаем настройки из окружения
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
session_str = os.environ.get('SESSION_STRING')
bot_username = os.environ.get('BOT_USERNAME', 'happygalaxy_bot')

# Инициализация
client = TelegramClient(StringSession(session_str), api_id, api_hash)

async def shop_routine():
    print("--- Запуск цикла покупки ---")
    try:
        async with client.conversation(bot_username, timeout=30) as conv:
            # 1. Отправляем команду
            await conv.send_message('/shop')
            resp1 = await conv.get_response()
            
            # 2. Нажимаем кнопку товара
            await resp1.click(data=b'get_product|119|1')
            
            # 3. Пауза перед подтверждением
            await asyncio.sleep(2) 
            
            # 4. Нажимаем подтверждение
            resp2 = await conv.get_response()
            await resp2.click(data=b'buy_product|119|')
            
            print("Результат: Покупка успешно совершена!")
    except Exception as e:
        print(f"Ошибка в процессе: {e}")

async def main():
    await client.start()
    print("Юзербот успешно запущен!")
    
    # проверка при старте
    print("Выполняю однократный тестовый прогон...")
    await shop_routine()
    
    # Настройка планировщика мск
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(shop_routine, 'cron', hour=15, minute=0)
    scheduler.add_job(shop_routine, 'cron', hour=18, minute=0)
    
    scheduler.start()
    print("Планировщик запущен. Ожидаю расписания.")
    
    # Работаем братья
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
