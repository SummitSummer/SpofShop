import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command, StateFilter
from aiogram import F
from config import BOT_TOKEN, ADMIN_ID
from handlers import (
    cmd_start, handle_order_subscription, handle_support, handle_faq, handle_back_to_menu,
    process_plan_selection, process_spotify_login, process_payment_completed,
    process_start_over, handle_unknown_message, cmd_admin_orders
)
from states import OrderState
from models import User, db, init_default_data
from app import app

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def setup_handlers(dp: Dispatcher):
    """Регистрация обработчиков"""
    # Команды
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_admin_orders, Command("orders"))
    
    # Callback-обработчики главного меню
    dp.callback_query.register(
        handle_order_subscription,
        F.data == "order_subscription"
    )
    
    dp.callback_query.register(
        handle_support,
        F.data == "support"
    )
    
    dp.callback_query.register(
        handle_faq,
        F.data == "faq"
    )
    
    dp.callback_query.register(
        handle_back_to_menu,
        F.data == "back_to_menu"
    )
    
    # Callback-обработчики заказа
    dp.callback_query.register(
        process_plan_selection,
        F.data.startswith("select_plan_"),
        OrderState.choosing_subscription
    )
    
    dp.callback_query.register(
        process_payment_completed,
        F.data == "payment_completed",
        OrderState.payment_processing
    )
    
    dp.callback_query.register(
        process_start_over,
        F.data == "start_over"
    )
    
    # Обработчики текстовых сообщений по состояниям
    dp.message.register(
        process_spotify_login,
        OrderState.entering_spotify_login
    )
    
    # Обработчик неизвестных сообщений
    dp.message.register(handle_unknown_message)

async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    logger.info("Бот запущен и готов к работе!")
    
    # Initialize database with default data
    with app.app_context():
        init_default_data()
        db.session.commit()
    
    # Уведомляем администратора о запуске
    try:
        await bot.send_message(
            ADMIN_ID,
            "🤖 Бот Spotify Family запущен и готов к приему заказов!"
        )
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление администратору: {e}")

async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info("Бот остановлен")

async def main():
    """Главная функция запуска бота"""
    logger.info("Инициализация Spotify Family Bot...")
    
    # Проверяем наличие токена
    if BOT_TOKEN == "your_bot_token_here":
        logger.error("❌ Не установлен токен бота! Установите переменную окружения BOT_TOKEN")
        return
    
    if ADMIN_ID == "123456789":
        logger.warning("⚠️ Не установлен ID администратора! Установите переменную окружения ADMIN_ID")
    
    # Создаем бота и диспетчер
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрируем обработчики
    await setup_handlers(dp)
    
    # Запускаем бота
    logger.info("Запуск бота...")
    await on_startup(bot)
    
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await on_shutdown(bot)
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
