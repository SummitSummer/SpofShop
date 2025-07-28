from aiogram.fsm.state import State, StatesGroup

class OrderState(StatesGroup):
    """Состояния для процесса заказа"""
    choosing_subscription = State()
    entering_spotify_login = State()
    payment_processing = State()

class AdminState(StatesGroup):
    """Состояния для админ функций"""
    broadcast_message = State()
    broadcast_confirm = State()
