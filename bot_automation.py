import os
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- НАСТРОЙКИ ---
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
session_str = os.environ.get('SESSION_STRING')
bot_username = os.environ.get('BOT_USERNAME', 'happygalaxy_bot')

client = TelegramClient(StringSession(session_str), api_id, api_hash)

async def step_by_step_navigation():
    print("Начинаю навигацию...")
    
    async with client.conversation(bot_username, timeout=10) as conv:
        while True:
            # 1. Принудительная отправка /shop в начале каждой итерации
            await conv.send_message('/shop')
            resp = await conv.get_response()
            
            if not resp.buttons:
                print("Кнопок нет, завершаю.")
                break
                
            buttons_data = [b.data for row in resp.buttons for b in row]
            
            # 2. Логика принятия решений
            
            # Если есть товар 119 -> ПОКУПКА
            if b'get_product|119|1' in buttons_data:
                print("Нашел товар 119, выбираю...")
                await resp.click(data=b'get_product|119|1')
                buy_resp = await conv.get_response()
                await buy_resp.click(data=b'buy_product|119|')
                print("Товар куплен!")
                break
            
            # Если есть товар 135 -> Переход к 3 (Страница 2)
            elif b'get_product|135|1' in buttons_data:
                print("Вижу товар 135 (Стр 2), нажимаю переход...")
                await resp.click(data=b'all_products|3')
                # После клика цикл вернется в начало и принудительно отправит /shop
                continue 
            
            # Если есть товар 151 -> Переход к 2 (Страница 1)
            elif b'get_product|151|1' in buttons_data:
                print("Вижу товар 151 (Стр 1), нажимаю переход...")
                await resp.click(data=b'all_products|2')
                # После клика цикл вернется в начало и принудительно отправит /shop
                continue
                
            else:
                print("Цель не найдена на текущей странице.")
                break

async def main():
    await client.start()
    await step_by_step_navigation()
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
    
