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

async def fast_shop_navigation(conv):
    """
    Листание страниц через жесткий сброс /shop.
    Без КД, максимально быстро.
    """
    print("--- АГРЕССИВНЫЙ СКАНИНГ СТРАНИЦ ---")
    
    # Схема переходов: [id страницы, на которую жмем]
    # Если на странице 1, жмем all_products|2, потом снова /shop и т.д.
    pages_to_check = [b'all_products|2', b'all_products|3']
    
    for page_btn in pages_to_check:
        await conv.send_message('/shop')
        resp = await conv.get_response()
        # Мгновенный клик без ожидания
        await resp.click(data=page_btn)
        print(f"Перешли на {page_btn.decode('utf-8')}")

async def execute_purchase():
    print("--- ВЫПОЛНЕНИЕ ЗАКУПА ---")
    try:
        async with client.conversation(bot_username, timeout=30) as conv:
            # 1. Листаем без КД через /shop
            await fast_shop_navigation(conv)
            
            # 2. Выбираем товар (после этого /shop уже НЕ ДЕЛАЕМ)
            await conv.send_message('/shop')
            resp = await conv.get_response()
            
            # Покупка
            resp = await resp.click(data=b'get_product|119|1')
            
            # 3. Финальное подтверждение (здесь уже по классике с паузой)
            resp = await conv.get_response()
            await resp.click(data=b'buy_product|119|')
            print("Успешный закуп!")
            
    except Exception as e:
        print(f"Ошибка: {e}")

async def main():
    await client.start()
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    # Расписание за 2 минуты и в 15/18
    scheduler.add_job(execute_purchase, 'cron', hour=14, minute=58)
    scheduler.add_job(execute_purchase, 'cron', hour=15, minute=0)
    scheduler.add_job(execute_purchase, 'cron', hour=17, minute=58)
    scheduler.add_job(execute_purchase, 'cron', hour=18, minute=0)
    
    scheduler.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
