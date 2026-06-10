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

async def fast_purchase():
    print("--- ЗАПУСК ЗАКУПА (Задержка 0.67с) ---")
    try:
        async with client.conversation(bot_username, timeout=20) as conv:
            await conv.send_message('/shop')
            resp = await conv.get_response()
            
            # --- УВЕРЕННЫЕ КЛИКИ ---
            await resp.click(data=b'all_products|2')
            await asyncio.sleep(0.67)
            
            await resp.click(data=b'all_products|3')
            await asyncio.sleep(0.67)
            
            await resp.click(data=b'get_product|119|1')
            await asyncio.sleep(0.67)
            
            # Финальное подтверждение
            resp2 = await conv.get_response()
            await resp2.click(data=b'buy_product|119|')
            
            print("Готово! Покупка прошла успешно.")
    except Exception as e:
        print(f"Ошибка при покупке: {e}")

async def main():
    await client.start()
    print("Бот авторизован и запущен.")
    
    # Проверка при старте
    await fast_purchase()
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(fast_purchase, 'cron', hour=15, minute=0, second=0)
    scheduler.add_job(fast_purchase, 'cron', hour=18, minute=0, second=0)
    
    scheduler.start()
    print("Планировщик активен. Жду 15:00 и 18:00.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
