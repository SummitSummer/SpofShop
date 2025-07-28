"""
Простой запуск бота без токена для демонстрации
"""
import asyncio
import logging
from datetime import datetime
from app import app, db
from models import User, Order, SubscriptionPlan, init_default_data
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DemoBot:
    """Демо-версия бота для тестирования без токена"""
    
    def __init__(self):
        self.running = False
        
    def start_demo_mode(self):
        """Запуск демо-режима с созданием тестовых данных"""
        logger.info("Запуск бота в демо-режиме...")
        
        with app.app_context():
            # Создаем тестовых пользователей
            demo_users = [
                {
                    'id': 123456789,
                    'username': 'demo_user1',
                    'first_name': 'Александр',
                    'last_name': 'Петров'
                },
                {
                    'id': 987654321,
                    'username': 'demo_user2', 
                    'first_name': 'Мария',
                    'last_name': 'Иванова'
                },
                {
                    'id': 555666777,
                    'username': 'demo_user3',
                    'first_name': 'Дмитрий',
                    'last_name': 'Сидоров'
                }
            ]
            
            for user_data in demo_users:
                existing_user = User.query.filter_by(id=user_data['id']).first()
                if not existing_user:
                    user = User()
                    user.id = user_data['id']
                    user.username = user_data['username']
                    user.first_name = user_data['first_name']
                    user.last_name = user_data['last_name']
                    user.language_code = 'ru'
                    user.last_activity = datetime.utcnow()
                    db.session.add(user)
            
            # Создаем тестовые заказы
            plans = SubscriptionPlan.query.all()
            if plans:
                for i, user_data in enumerate(demo_users):
                    order_id = f"ORDER_{10000 + i + 1:05d}"
                    existing_order = Order.query.filter_by(id=order_id).first()
                    if not existing_order:
                        order = Order()
                        order.id = order_id
                        order.user_id = user_data['id']
                        order.plan_id = plans[i % len(plans)].id
                        order.total_amount = plans[i % len(plans)].price
                        order.created_at = datetime.utcnow()
                        db.session.add(order)
            
            db.session.commit()
            logger.info("Демо-данные созданы успешно")
        
        self.running = True
        logger.info("Бот запущен в демо-режиме. Данные обновляются через админ-панель.")
        
        # Запускаем фоновую задачу для имитации активности
        def background_task():
            while self.running:
                time.sleep(30)  # Обновляем каждые 30 секунд
                try:
                    with app.app_context():
                        # Обновляем время последней активности пользователей
                        User.query.update({User.last_activity: datetime.utcnow()})
                        db.session.commit()
                except Exception as e:
                    logger.error(f"Ошибка в фоновой задаче: {e}")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()
        
        return "Демо-бот запущен. Проверьте админ-панель для управления."

    def stop(self):
        self.running = False
        logger.info("Демо-бот остановлен")

# Глобальный экземпляр бота
demo_bot = DemoBot()

def start_demo_bot():
    """Функция для запуска демо-бота"""
    return demo_bot.start_demo_mode()

def stop_demo_bot():
    """Функция для остановки демо-бота"""
    demo_bot.stop()

if __name__ == "__main__":
    start_demo_bot()
    
    try:
        # Держим программу активной
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_demo_bot()
        print("Демо-бот остановлен")