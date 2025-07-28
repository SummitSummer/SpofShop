"""
Telegram bot handlers for Spotify subscription bot
Simplified version without payment system
"""
import logging
from datetime import datetime
from aiogram import types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app import app, db
from models import User, Order, SubscriptionPlan, OrderStatus

logger = logging.getLogger(__name__)

# FSM States
class OrderState(StatesGroup):
    choosing_plan = State()
    awaiting_contact = State()
    
# Keyboards
def get_main_keyboard():
    """Main menu keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 Заказать подписку", callback_data="order_subscription")],
        [InlineKeyboardButton(text="❓ FAQ", callback_data="faq")],
        [InlineKeyboardButton(text="👤 Поддержка", callback_data="support")]
    ])
    return keyboard

def get_subscription_plans_keyboard():
    """Subscription plans selection keyboard"""
    buttons = []
    with app.app_context():
        plans = SubscriptionPlan.query.filter_by(is_active=True).all()
        for plan in plans:
            text = f"{plan.name} - {plan.price}₽"
            buttons.append([InlineKeyboardButton(text=text, callback_data=f"plan_{plan.id}")])
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_keyboard():
    """Back to main menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_menu")]
    ])

# Helper functions
def create_or_update_user(telegram_user):
    """Create or update user in database"""
    with app.app_context():
        user = User.query.filter_by(id=telegram_user.id).first()
        if not user:
            user = User()
            user.id = telegram_user.id
            user.username = telegram_user.username
            user.first_name = telegram_user.first_name
            user.last_name = telegram_user.last_name
            user.language_code = telegram_user.language_code or 'ru'
            db.session.add(user)
        else:
            user.username = telegram_user.username
            user.first_name = telegram_user.first_name
            user.last_name = telegram_user.last_name
            user.last_activity = datetime.utcnow()
        
        db.session.commit()
        return user

# Handlers
async def cmd_start(message: types.Message, state: FSMContext):
    """Start command handler"""
    try:
        user = create_or_update_user(message.from_user)
        await state.clear()
        
        welcome_text = (
            "🎵 <b>Добро пожаловать в Spotify Family Bot!</b> 🎵\n\n"
            "Здесь вы можете заказать доступ к Spotify Premium по выгодной цене!\n\n"
            "💎 <b>Что вы получите:</b>\n"
            "• Безлимитное прослушивание музыки\n"
            "• Без рекламы\n"
            "• Высокое качество звука\n"
            "• Загрузка музыки офлайн\n"
            "• Доступ ко всем функциям Spotify Premium\n\n"
            "Выберите действие из меню ниже:"
        )
        
        await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in cmd_start: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

async def handle_order_subscription(callback: types.CallbackQuery, state: FSMContext):
    """Handle subscription order"""
    try:
        await callback.answer()
        
        text = (
            "📋 <b>Выберите план подписки:</b>\n\n"
            "💡 <i>Чем дольше период, тем выгоднее цена!</i>"
        )
        
        await callback.message.edit_text(
            text, 
            reply_markup=get_subscription_plans_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(OrderState.choosing_plan)
        
    except Exception as e:
        logger.error(f"Error in handle_order_subscription: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)

async def handle_plan_selection(callback: types.CallbackQuery, state: FSMContext):
    """Handle subscription plan selection"""
    try:
        await callback.answer()
        
        plan_id = callback.data.replace("plan_", "")
        
        with app.app_context():
            plan = SubscriptionPlan.query.filter_by(id=plan_id).first()
            if not plan:
                await callback.answer("План не найден", show_alert=True)
                return
                
            # Create order
            order_count = Order.query.count() + 1
            order_id = f"ORDER_{order_count:05d}"
            
            order = Order()
            order.id = order_id
            order.user_id = callback.from_user.id
            order.plan_id = plan.id
            order.total_amount = plan.price
            order.status = OrderStatus.CREATED
            order.created_at = datetime.utcnow()
            
            db.session.add(order)
            db.session.commit()
            
            text = (
                f"✅ <b>Заказ создан!</b>\n\n"
                f"🆔 <b>Номер заказа:</b> <code>{order_id}</code>\n"
                f"📦 <b>План:</b> {plan.name}\n"
                f"💰 <b>Стоимость:</b> {plan.price}₽\n\n"
                f"📞 <b>Что делать дальше:</b>\n"
                f"1. Свяжитесь с поддержкой @chanceofrain\n"
                f"2. Сообщите номер заказа: <code>{order_id}</code>\n"
                f"3. Администратор обработает ваш заказ\n\n"
                f"<i>💡 В демо-режиме платежи отключены</i>"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👤 Связаться с поддержкой", url="https://t.me/chanceofrain")],
                [InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_menu")]
            ])
            
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
            await state.clear()
            
    except Exception as e:
        logger.error(f"Error in handle_plan_selection: {e}")
        await callback.answer("Произошла ошибка при создании заказа", show_alert=True)

async def handle_faq(callback: types.CallbackQuery):
    """Handle FAQ"""
    try:
        await callback.answer()
        
        faq_text = (
            "❓ <b>Часто задаваемые вопросы</b>\n\n"
            "<b>Q: Как работает Spotify Family?</b>\n"
            "A: Вы получаете доступ к семейной подписке со всеми премиум функциями.\n\n"
            "<b>Q: Безопасно ли это?</b>\n"
            "A: Да, мы используем официальные методы и не нарушаем правила Spotify.\n\n"
            "<b>Q: Как долго действует подписка?</b>\n"
            "A: Согласно выбранному вами плану (1, 3, 6 или 12 месяцев).\n\n"
            "<b>Q: Что если возникнут проблемы?</b>\n"
            "A: Обращайтесь в поддержку @chanceofrain - мы решим любые вопросы.\n\n"
            "<b>Q: Можно ли продлить подписку?</b>\n"
            "A: Да, обращайтесь к нам за месяц до окончания."
        )
        
        await callback.message.edit_text(faq_text, reply_markup=get_back_keyboard(), parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in handle_faq: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)

async def handle_support(callback: types.CallbackQuery):
    """Handle support contact"""
    try:
        await callback.answer()
        
        support_text = (
            "👤 <b>Поддержка</b>\n\n"
            "По всем вопросам обращайтесь к администратору:\n"
            "👨‍💻 @chanceofrain\n\n"
            "📞 <b>Мы поможем с:</b>\n"
            "• Оформление заказа\n"
            "• Технические вопросы\n"
            "• Проблемы с подпиской\n"
            "• Возврат средств\n\n"
            "⏰ <b>Время ответа:</b> обычно в течение часа"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Написать в поддержку", url="https://t.me/chanceofrain")],
            [InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_menu")]
        ])
        
        await callback.message.edit_text(support_text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in handle_support: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)

async def handle_back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """Return to main menu"""
    try:
        await callback.answer()
        await state.clear()
        
        welcome_text = (
            "🎵 <b>Spotify Family Bot</b> 🎵\n\n"
            "Выберите действие из меню:"
        )
        
        await callback.message.edit_text(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in handle_back_to_menu: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)

def register_handlers(dp):
    """Register all bot handlers"""
    # Commands
    dp.message.register(cmd_start, Command("start"))
    
    # Callbacks
    dp.callback_query.register(handle_order_subscription, F.data == "order_subscription")
    dp.callback_query.register(handle_plan_selection, F.data.startswith("plan_"))
    dp.callback_query.register(handle_faq, F.data == "faq")
    dp.callback_query.register(handle_support, F.data == "support")
    dp.callback_query.register(handle_back_to_menu, F.data == "back_to_menu")
    
    logger.info("Bot handlers registered successfully")