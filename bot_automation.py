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

# Универсальная функция нажатия с задержкой 3с
async def click_if_exists(message, data_string, delay=3.0):
    for row in message.buttons:
        for button in row:
            if button.data == data_string:
                print(f"Найдена: {data_string.decode('utf-8')}. Нажимаю...")
                new_message = await message.click(data=data_string)
                await asyncio.sleep(delay)
                return new_message, True  # Возвращаем флаг True, что кнопка найдена
    print(f"Кнопка {data_string.decode('utf-8')} не найдена.")
    return message, False

# Функция покупки (вынесена отдельно для использования в обоих случаях)
async def perform_purchase(conv):
    print("--- Начинаю процесс покупки ---")
    await conv.send_message('/shop')
    resp = await conv.get_response()
    
    resp = await click_if_exists(resp, b'get_product|119|1')
    resp = await conv.get_response()
    await click_if_exists(resp, b'buy_product|119|')
    print("Закуп успешно завершен!")

# Функция листания с проверкой на 4 страницу
async def prepare_shop():
    print("--- Процесс поиска 4 страницы ---")
    try:
        async with client.conversation(bot_username, timeout=45) as conv:
            await conv.send_message('/shop')
            resp = await conv.get_response()
            
            # Проверяем страницу 2
            resp, found2 = await click_if_exists(resp, b'all_products|2')
            
            # Проверяем страницу 3
            resp, found3 = await click_if_exists(resp, b'all_products|3')
            
            # Проверяем страницу 4 -> ЕСЛИ НАШЛИ, СРАЗУ ПОКУПАЕМ
            resp, found4 = await click_if_exists(resp, b'all_products|4')
            if found4:
                print("Найдена страница 4! Перехожу к покупке.")
                await perform_purchase(conv)
                
    except Exception as e:
        print(f"Ошибка в процессе подготовки: {e}")

async def main():
    await client.start()
    print("Бот запущен. Автоматическая проверка...")
    
    # Первичная проверка
    await prepare_shop()
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(prepare_shop, 'cron', hour=14, minute=58)
    scheduler.add_job(prepare_shop, 'cron', hour=17, minute=58)
    scheduler.add_job(perform_purchase, 'cron', hour=15, minute=0, second=0)
    scheduler.add_job(perform_purchase, 'cron', hour=18, minute=0, second=0)
    
    scheduler.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
