from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import SUBSCRIPTION_PLANS

def get_main_menu_keyboard():
    """Создает главное меню бота"""
    buttons = [
        [InlineKeyboardButton(text="🎟 Оформить подписку", callback_data="order_subscription")],
        [InlineKeyboardButton(text="💬 Support", callback_data="support")],
        [InlineKeyboardButton(text="📖 Наш FAQ", callback_data="faq")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_subscription_keyboard():
    """Создает клавиатуру с вариантами подписки"""
    buttons = []
    
    for plan_id, plan_info in SUBSCRIPTION_PLANS.items():
        button_text = f"💚{plan_info['name']}💚 — {plan_info['price']}₽"
        callback_data = f"select_plan_{plan_id}"
        buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
    
    # Добавляем кнопку "Назад"
    buttons.append([InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_payment_keyboard(payment_url):
    """Создает клавиатуру с кнопкой оплаты"""
    buttons = [
        [InlineKeyboardButton(text="💳 Оплатить", url=payment_url)],
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="payment_completed")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_back_to_start_keyboard():
    """Клавиатура для возврата к началу"""
    buttons = [
        [InlineKeyboardButton(text="🔄 Начать заново", callback_data="start_over")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_back_to_menu_keyboard():
    """Клавиатура для возврата в главное меню"""
    buttons = [
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
