from aiogram.fsm.state import State, StatesGroup

class OrderState(StatesGroup):
    """Состояния для обработки заказа"""
    choosing_subscription = State()  # Выбор подписки
    entering_spotify_login = State()  # Ввод логина Spotify
    payment_processing = State()     # Обработка оплаты
    order_completed = State()        # Заказ завершен
