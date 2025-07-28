from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard():
    """Главное меню бота"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 Оформить подписку", callback_data="order_subscription")],
        [InlineKeyboardButton(text="💬 Поддержка", callback_data="support")],
        [InlineKeyboardButton(text="❓ FAQ", callback_data="faq")]
    ])
    return keyboard

def get_subscription_keyboard():
    """Клавиатура выбора подписки"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 месяц - 150₽", callback_data="select_plan_1_month")],
        [InlineKeyboardButton(text="3 месяца - 370₽", callback_data="select_plan_3_months")],
        [InlineKeyboardButton(text="6 месяцев - 690₽", callback_data="select_plan_6_months")],
        [InlineKeyboardButton(text="12 месяцев - 1300₽", callback_data="select_plan_12_months")],
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
    ])
    return keyboard

def get_payment_keyboard(payment_url):
    """Клавиатура для оплаты"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Перейти к оплате", url=payment_url)],
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="payment_completed")],
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
    ])
    return keyboard

def get_back_to_menu_keyboard():
    """Кнопка возврата в главное меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
    ])
    return keyboard

def get_back_to_start_keyboard():
    """Кнопка начать заново"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Начать заново", callback_data="start_over")]
    ])
    return keyboard
