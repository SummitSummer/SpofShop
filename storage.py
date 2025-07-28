import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OrderStorage:
    """Простое хранилище заказов в памяти"""
    
    def __init__(self):
        self.orders = {}  # user_id -> order_data
        self.order_counter = 1
    
    def create_order(self, user_id: int, user_data: Dict[str, Any]) -> str:
        """Создает новый заказ"""
        order_id = f"ORDER_{self.order_counter:05d}"
        self.order_counter += 1
        
        order_data = {
            "order_id": order_id,
            "user_id": user_id,
            "username": user_data.get("username", ""),
            "first_name": user_data.get("first_name", ""),
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "subscription_plan": None,
            "spotify_login": None,
            "payment_url": None
        }
        
        self.orders[user_id] = order_data
        logger.info(f"Создан заказ {order_id} для пользователя {user_id}")
        return order_id
    
    def update_order(self, user_id: int, **kwargs):
        """Обновляет данные заказа"""
        if user_id in self.orders:
            self.orders[user_id].update(kwargs)
            logger.info(f"Обновлен заказ для пользователя {user_id}: {kwargs}")
    
    def get_order(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает заказ по ID пользователя"""
        return self.orders.get(user_id)
    
    def complete_order(self, user_id: int):
        """Завершает заказ"""
        if user_id in self.orders:
            self.orders[user_id]["status"] = "completed"
            self.orders[user_id]["completed_at"] = datetime.now().isoformat()
            logger.info(f"Заказ для пользователя {user_id} завершен")
    
    def get_all_orders(self) -> Dict[int, Dict[str, Any]]:
        """Возвращает все заказы"""
        return self.orders.copy()

# Глобальный экземпляр хранилища
order_storage = OrderStorage()
