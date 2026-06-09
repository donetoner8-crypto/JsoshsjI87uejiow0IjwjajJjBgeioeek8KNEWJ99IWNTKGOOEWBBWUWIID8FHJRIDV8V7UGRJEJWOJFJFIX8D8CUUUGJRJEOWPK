import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
session_str = os.environ.get('SESSION_STRING')
bot_username = os.environ.get('BOT_USERNAME', 'happygalaxy_bot')

client = TelegramClient(StringSession(session_str), api_id, api_hash)

async def shop_routine():
    print("Запуск цикла покупки...")
    try:
        async with client.conversation(bot_username, timeout=30) as conv:
            # 1. команду
            await conv.send_message('/shop')
            resp1 = await conv.get_response()
            
            # 2. кнопку товара
            await resp1.click(data=b'get_product|119|1')
            await asyncio.sleep(2) 
            
            # 3. кнопку подтверждения
            resp2 = await conv.get_response()
            await resp2.click(data=b'buy_product|119|')
            
            print("Успех: Покупка совершена!")
    except Exception as e:
        print(f"Ошибка в процессе: {e}")

async def main():
    await client.start()
    print("Юзербот запущен в облаке!")
    
    # Настройка планировщика мск
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(shop_routine, 'cron', hour=15, minute=0)
    scheduler.add_job(shop_routine, 'cron', hour=18, minute=0)
    
    scheduler.start()
    
    # Держим процесс
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
