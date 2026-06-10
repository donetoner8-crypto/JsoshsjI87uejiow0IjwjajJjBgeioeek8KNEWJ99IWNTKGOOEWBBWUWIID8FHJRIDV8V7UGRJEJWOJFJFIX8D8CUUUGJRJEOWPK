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

# Агрессивная навигация: сброс через /shop и моментальный клик
async def fast_navigate(conv, data_string):
    await conv.send_message('/shop')
    resp = await conv.get_response()
    await resp.click(data=data_string)
    print(f"Сброс и переход: {data_string.decode('utf-8')}")

# Основной поток закупа
async def run_purchase_flow():
    print("--- ЗАПУСК АГРЕССИВНОГО ЗАКУПА ---")
    try:
        async with client.conversation(bot_username, timeout=30) as conv:
            # 1. Мгновенная навигация без пауз
            await fast_navigate(conv, b'all_products|2')
            await fast_navigate(conv, b'all_products|3')
            
            # 2. Переход к покупке
            await conv.send_message('/shop')
            resp = await conv.get_response()
            
            # Выбор товара (без задержек)
            resp = await resp.click(data=b'get_product|119|1')
            
            # 3. Финальное подтверждение (здесь задержка минимальна для обработки транзакции)
            resp = await conv.get_response()
            await resp.click(data=b'buy_product|119|')
            print("Успех: Товар куплен!")
            
    except Exception as e:
        print(f"Ошибка в процессе: {e}")

async def main():
    await client.start()
    print("Бот готов к работе.")
    
    # Первичный прогон при старте
    await run_purchase_flow()
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    # Расписание (за 2 минуты до закупа и в ровное время)
    scheduler.add_job(run_purchase_flow, 'cron', hour=14, minute=58)
    scheduler.add_job(run_purchase_flow, 'cron', hour=15, minute=0)
    scheduler.add_job(run_purchase_flow, 'cron', hour=17, minute=58)
    scheduler.add_job(run_purchase_flow, 'cron', hour=18, minute=0)
    
    scheduler.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
