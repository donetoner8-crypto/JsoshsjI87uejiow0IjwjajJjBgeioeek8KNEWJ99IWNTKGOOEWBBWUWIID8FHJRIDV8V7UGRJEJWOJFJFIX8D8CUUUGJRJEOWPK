import os
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- НАСТРОЙКИ ---
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
session_str = os.environ.get('SESSION_STRING')
bot_username = os.environ.get('BOT_USERNAME', 'happygalaxy_bot')

client = TelegramClient(StringSession(session_str), api_id, api_hash)

async def navigate_and_buy(conv):
    """Навигация по ID товаров-якорей на страницах"""
    # Отправляем /shop
    await conv.send_message('/shop')
    resp = await conv.get_response()
    
    if not resp.buttons:
        return "no_buttons"

    # Собираем данные всех кнопок
    buttons_data = [b.data for row in resp.buttons for b in row]
    
    # 1. ПРОВЕРКА ЦЕЛИ: Если видим наш товар 119 -> МЫ НА МЕСТЕ, ПОКУПАЕМ
    if b'get_product|119|1' in buttons_data:
        print("Вижу целевой товар [119] -> Выбираю и покупаю!")
        resp = await resp.click(data=b'get_product|119|1')
        resp = await conv.get_response()
        await resp.click(data=b'buy_product|119|')
        return "bought"

    # 2. ПРОВЕРКА 2 СТРАНИЦЫ: Если видим товар 135 -> МЫ НА СТР 2, ЖМЕМ 3
    if b'get_product|135|1' in buttons_data:
        print("Вижу товар [135] (Страница 2) -> Жму all_products|3")
        await resp.click(data=b'all_products|3')
        return "navigated"

    # 3. ПРОВЕРКА 1 СТРАНИЦЫ: Если видим товар 151 -> МЫ НА СТР 1, ЖМЕМ 2
    if b'get_product|151|1' in buttons_data:
        print("Вижу товар [151] (Страница 1) -> Жму all_products|2")
        await resp.click(data=b'all_products|2')
        return "navigated"
    
    return "not_found"

async def test_full_cycle():
    """Прогоняет всю цепочку при запуске бота"""
    print("--- ПРОВЕРКА ПРИ ЗАПУСКЕ: ПРОГОН ПО ТОВАРАМ ---")
    step = 0
    while step < 10: # Лимит шагов от зависания
        step += 1
        try:
            async with client.conversation(bot_username, timeout=5) as conv:
                status = await navigate_and_buy(conv)
                
                if status == "bought":
                    print("Тест завершен: Товар успешно куплен!")
                    break
                elif status == "navigated":
                    print("Тест: Переход выполнен, моментально шлю /shop...")
                    continue # Моментальный рестарт цикла с отправкой /shop
                else:
                    print("Тест: Цепочка прервалась, нужных товаров-якорей нет на странице.")
                    break
        except Exception as e:
            print(f"Ошибка в тестовом цикле: {e}")
            break

async def start_aggressive_mode(target_hour):
    """Боевой пулемет"""
    print(f"--- АГРЕССИВНЫЙ РЕЖИМ (Цель: {target_hour}:01) ---")
    while True:
        now = datetime.now()
        
        # Стоп-кран в 01 минуту
        if now.hour == target_hour and now.minute >= 1:
            print("Время вышло. Остановка цикла.")
            break
        
        try:
            async with client.conversation(bot_username, timeout=3) as conv:
                status = await navigate_and_buy(conv)
                
                if status == "bought": 
                    print("Товар успешно куплен! Выхожу из цикла.")
                    break
                elif status == "navigated":
                    # Если нажали кнопку перехода, сразу летим на новую итерацию отправлять /shop
                    continue
                
        except Exception:
            # Ошибки связи игнорим, просто пробуем еще раз
            pass
        
        # Задержка ТОЛЬКО если нужных товаров вообще нет (ждем появления)
        await asyncio.sleep(0.1)

async def main():
    await client.start()
    print("Бот авторизован и готов к работе.")
    
    # --- ПРОВЕРКА ПРИ ЗАПУСКЕ ---
    await test_full_cycle()
    # -----------------------------
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    # Расписание запуска
    scheduler.add_job(start_aggressive_mode, 'cron', hour=14, minute=59, second=40, args=[15])
    scheduler.add_job(start_aggressive_mode, 'cron', hour=17, minute=59, second=40, args=[18])
    
    scheduler.start()
    print("Расписание активно. Ожидаю времени закупа...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
    
