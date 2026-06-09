import os
import asyncio
from telethon import TelegramClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Получаем настройки из переменных окружения (вводим их в панели Railway)
# API_ID и API_HASH получаются на my.telegram.org
api_id = int(os.environ.get('API_ID', 0))
api_hash = os.environ.get('API_HASH', '')
bot_username = os.environ.get('BOT_USERNAME', 'happygalaxy_bot')

# Имя сессии - файл создастся автоматически при первом запуске
client = TelegramClient('my_session', api_id, api_hash)

async def shop_routine():
    print("Начинаю выполнение цикла покупки...")
    try:
        # Устанавливаем соединение с ботом
        async with client.conversation(bot_username, timeout=30) as conv:
            # 1. Отправляем команду в магазин
            await conv.send_message('/shop')
            
            # 2. Ждем ответ с товарами
            resp1 = await conv.get_response()
            
            # 3. Нажимаем кнопку выбора товара (первый клик)
            # b'' превращает текст в байты, что необходимо для Telegram API
            await resp1.click(data=b'get_product|119|1')
            
            # Пауза 2 секунды, чтобы бот успел обработать выбор
            await asyncio.sleep(2) 
            
            # 4. Ждем второй ответ с кнопкой подтверждения
            resp2 = await conv.get_response()
            
            # 5. Нажимаем кнопку подтверждения (второй клик)
            await resp2.click(data=b'buy_product|119|')
            
            print("Покупка успешно выполнена!")
            
    except Exception as e:
        print(f"Ошибка в процессе покупки: {e}")

async def main():
    # Запуск 
    await client.start()
    print("Юзербот запущен и ожидает времени...")
    
    # Настройка планировщика
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(shop_routine, 'cron', hour=15, minute=0)
    scheduler.add_job(shop_routine, 'cron', hour=18, minute=0)
    
    scheduler.start()
    
    # Работаем
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
  
