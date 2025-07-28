import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from config import SUBSCRIPTION_PLANS, ADMIN_ID
from states import OrderState
from keyboards import (
    get_main_menu_keyboard, get_subscription_keyboard, get_payment_keyboard,
    get_back_to_start_keyboard, get_back_to_menu_keyboard
)
from models import User, Order, SubscriptionPlan, db
from app import app
from digiseller import generate_payment_url
from datetime import datetime

logger = logging.getLogger(__name__)

def get_or_create_user(telegram_user):
    """Получить или создать пользователя в базе данных"""
    with app.app_context():
        user = User.query.filter_by(id=telegram_user.id).first()
        if not user:
            user = User(
                id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                language_code=telegram_user.language_code
            )
            db.session.add(user)
            db.session.commit()
        else:
            # Обновляем данные пользователя
            user.username = telegram_user.username
            user.first_name = telegram_user.first_name
            user.last_name = telegram_user.last_name
            user.last_activity = datetime.utcnow()
            db.session.commit()
        return user

async def cmd_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start - показывает главное меню с изображением"""
    # Очищаем предыдущие состояния
    await state.clear()
    
    # Регистрируем/обновляем пользователя
    user = get_or_create_user(message.from_user)
    
    welcome_text = (
        "🎵 **Добро пожаловать в Spotify Family Bot!** 🎵\n\n"
        "🔥 Получите доступ к **Spotify Premium** по лучшим ценам!\n\n"
        "✅ **Что вы получаете:**\n"
        "• Безлимитная музыка без рекламы\n"
        "• Высокое качество звука\n"
        "• Скачивание треков для офлайн прослушивания\n"
        "• Доступ ко всем функциям Spotify Premium\n\n"
        "💚 **Выберите действие:**"
    )
    
    keyboard = get_main_menu_keyboard()
    
    try:
        # Отправляем главное меню с изображением
        from aiogram.types import FSInputFile
        photo = FSInputFile("spotify_image.png")
        await message.answer_photo(
            photo=photo,
            caption=welcome_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки изображения в главном меню: {e}")
        # Если ошибка с изображением, отправляем только текст
        await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

async def handle_order_subscription(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки оформления подписки"""
    user = get_or_create_user(callback_query.from_user)
    
    subscription_text = (
        "🎵 **Выберите план подписки Spotify Premium:**\n\n"
        "💚 **Доступные варианты:**\n"
        "🔸 **1 месяц** — 150₽\n"
        "🔸 **3 месяца** — 370₽ *(экономия 80₽)*\n"
        "🔸 **6 месяцев** — 690₽ *(экономия 210₽)*\n"
        "🔸 **12 месяцев** — 1300₽ *(экономия 500₽)*\n\n"
        "✨ **Что включено в Premium:**\n"
        "• Безлимитная музыка без рекламы\n"
        "• Высокое качество звука (до 320 kbps)\n"
        "• Офлайн прослушивание\n"
        "• Пропуск треков без ограничений\n"
        "• Доступ к Spotify Connect\n\n"
        "💚 Выберите подходящий план:"
    )
    
    keyboard = get_subscription_keyboard()
    
    # Удаляем сообщение с изображением и отправляем новое текстовое
    if callback_query.message:
        await callback_query.message.delete()
        await callback_query.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=subscription_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    await state.set_state(OrderState.choosing_subscription)
    await callback_query.answer()

async def handle_support(callback_query: types.CallbackQuery):
    """Обработчик кнопки Support"""
    support_text = (
        "💬 **Поддержка**\n\n"
        "Если возникли дополнительные вопросы, обратитесь по этому контакту:\n\n"
        "👤 https://t.me/chanceofrain"
    )
    
    keyboard = get_back_to_menu_keyboard()
    
    if callback_query.message:
        # Удаляем сообщение с изображением и отправляем новое текстовое
        await callback_query.message.delete()
        await callback_query.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=support_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    await callback_query.answer()

async def handle_faq(callback_query: types.CallbackQuery):
    """Обработчик кнопки FAQ"""
    faq_text = (
        "📖 **Часто задаваемые вопросы**\n\n"
        "1️⃣ **Это официальная подписка?**\n"
        "— Да, это настоящая подписка Spotify Premium через семейный план.\n\n"
        "2️⃣ **Нужно ли что-то платить каждый месяц?**\n"
        "— Нет. Вы платите один раз за выбранный срок (1 / 3 / 6 / 12 месяцев).\n\n"
        "3️⃣ **Что мне нужно для подключения?**\n"
        "— Логин и пароль от Spotify аккаунта.\n\n"
        "4️⃣ **Как происходит добавление в семью?**\n"
        "— Мы отправляем приглашение в семью Spotify, вы подтверждаете адрес.\n\n"
        "5️⃣ **Это безопасно?**\n"
        "— Да. Данные используются только для добавления в семью и не передаются третьим лицам.\n\n"
        "6️⃣ **Сколько времени занимает подключение?**\n"
        "— От 5 до 30 минут. Иногда до 2 часов.\n\n"
        "7️⃣ **Что если меня удалят из семьи?**\n"
        "— Мы восстановим вас бесплатно, если срок ещё не истёк.\n\n"
        "8️⃣ **Можно ли продлить подписку?**\n"
        "— Да, просто оформите новый срок через бота."
    )
    
    keyboard = get_back_to_menu_keyboard()
    
    if callback_query.message:
        # Удаляем сообщение с изображением и отправляем новое текстовое
        await callback_query.message.delete()
        await callback_query.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=faq_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    await callback_query.answer()

async def handle_back_to_menu(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки возврата в главное меню"""
    await state.clear()
    
    welcome_text = (
        "🎵 **Добро пожаловать в Spotify Family Bot!** 🎵\n\n"
        "🔥 Получите доступ к **Spotify Premium** по лучшим ценам!\n\n"
        "✅ **Что вы получаете:**\n"
        "• Безлимитная музыка без рекламы\n"
        "• Высокое качество звука\n"
        "• Скачивание треков для офлайн прослушивания\n"
        "• Доступ ко всем функциям Spotify Premium\n\n"
        "💚 **Выберите действие:**"
    )
    
    keyboard = get_main_menu_keyboard()
    
    if callback_query.message:
        # Удаляем текущее сообщение и отправляем новое с изображением
        await callback_query.message.delete()
        try:
            # Отправляем главное меню с изображением
            from aiogram.types import FSInputFile
            photo = FSInputFile("spotify_image.png")
            await callback_query.bot.send_photo(
                chat_id=callback_query.message.chat.id,
                photo=photo,
                caption=welcome_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Ошибка отправки изображения в главном меню: {e}")
            # Если ошибка с изображением, отправляем только текст
            await callback_query.bot.send_message(
                chat_id=callback_query.message.chat.id,
                text=welcome_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
    
    await callback_query.answer()

async def process_plan_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора плана подписки"""
    plan_id = callback_query.data.replace("select_plan_", "") if callback_query.data else ""
    
    with app.app_context():
        plan = SubscriptionPlan.query.filter_by(id=plan_id).first()
        if not plan:
            await callback_query.answer("❌ Неверный план подписки")
            return
        
        # Создаем заказ в базе данных
        order_count = Order.query.count() + 1
        order_id = f"ORDER_{order_count:05d}"
        
        order = Order(
            id=order_id,
            user_id=callback_query.from_user.id,
            plan_id=plan_id,
            total_amount=plan.price,
            status='created'
        )
        db.session.add(order)
        db.session.commit()
        
        # Сохраняем ID заказа в состоянии
        await state.update_data(order_id=order_id, selected_plan=plan_id)
    
    # Запрашиваем логин от Spotify с подробными инструкциями
    text = (
        f"✅ **Выбрана подписка:** {plan.name} — {plan.price}₽\n\n"
        "📧 **Введите данные от Spotify:**\n\n"
        "⚠️ **ВАЖНО:**\n"
        "• Введите данные в формате: **логин:пароль**\n"
        "• Проверьте данные перед отправкой — **они должны быть точными**\n"
        "• Используйте **точно такой же** логин и пароль, как в приложении Spotify\n\n"
        "📝 **Пример:**\n"
        "• your_email@gmail.com:yourpassword123\n"
        "• spotify_username:yourpassword\n\n"
        "🔒 **Безопасность:** Данные используются только для добавления в семью и не передаются третьим лицам"
    )
    
    keyboard = get_back_to_menu_keyboard()
    
    if callback_query.message:
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    
    await state.set_state(OrderState.entering_spotify_login)
    await callback_query.answer()

async def process_spotify_login(message: types.Message, state: FSMContext):
    """Обработка ввода логина Spotify"""
    if not message.text:
        return
    
    spotify_login = message.text.strip()
    
    # Валидация формата логин:пароль
    if ":" not in spotify_login:
        await message.answer(
            "❌ Неверный формат данных. Введите в формате: логин:пароль\n\nПример: myemail@gmail.com:mypassword123",
            reply_markup=get_back_to_start_keyboard()
        )
        return
    
    login_parts = spotify_login.split(":", 1)
    if len(login_parts) != 2 or len(login_parts[0]) < 3 or len(login_parts[1]) < 3:
        await message.answer(
            "❌ Логин или пароль слишком короткие. Введите в формате: логин:пароль",
            reply_markup=get_back_to_start_keyboard()
        )
        return
    
    # Получаем данные заказа из состояния
    state_data = await state.get_data()
    order_id = state_data.get("order_id")
    
    with app.app_context():
        order = Order.query.filter_by(id=order_id).first()
        if not order:
            await message.answer("❌ Заказ не найден")
            return
        
        # Обновляем заказ с данными Spotify
        order.spotify_login = login_parts[0]
        order.spotify_password = login_parts[1]  # В реальном проекте следует шифровать
        
        # Генерируем ссылку на оплату через Digiseller
        try:
            payment_url = generate_payment_url(order)
            order.payment_url = payment_url
            order.status = 'awaiting_payment'
        except Exception as e:
            logger.error(f"Ошибка генерации ссылки на оплату: {e}")
            payment_url = f"https://payment-gateway.example.com/pay?order_id={order_id}&amount={order.total_amount}"
            order.payment_url = payment_url
        
        db.session.commit()
        
        plan = order.subscription_plan
    
    # Отправляем сообщение с оплатой
    payment_text = (
        f"💳 **К оплате:** {plan.price}₽\n\n"
        f"📋 **Детали заказа:**\n"
        f"• **Подписка:** {plan.name}\n"
        f"• **Spotify аккаунт:** {login_parts[0]}\n\n"
        "🔥 **Что делать дальше:**\n"
        "1️⃣ Нажмите кнопку **'💳 Оплатить'**\n"
        "2️⃣ Совершите платеж\n"
        "3️⃣ Нажмите **'✅ Я оплатил'**\n\n"
        "⚡️ После подтверждения оплаты вы получите доступ к Spotify Premium в течение 5-30 минут!"
    )
    
    keyboard = get_payment_keyboard(payment_url)
    
    await message.answer(payment_text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(OrderState.payment_processing)

async def process_payment_completed(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка подтверждения оплаты"""
    state_data = await state.get_data()
    order_id = state_data.get("order_id")
    
    with app.app_context():
        order = Order.query.filter_by(id=order_id).first()
        if not order:
            await callback_query.answer("❌ Заказ не найден")
            return
        
        # Обновляем статус заказа
        order.status = 'paid'
        db.session.commit()
    
    # Уведомляем пользователя
    success_text = (
        "✅ Заявка на оплату принята!\n\n"
        "📞 Администратор проверит платеж и свяжется с вами в ближайшее время для активации подписки.\n"
        "Обычно это занимает до 24 часов."
    )
    
    if callback_query.message:
        await callback_query.message.edit_text(success_text, reply_markup=get_back_to_start_keyboard())
    
    # Уведомляем администратора
    try:
        admin_msg = (
            f"🔔 **Новый заказ на проверку!**\n\n"
            f"**Заказ:** {order_id}\n"
            f"**Пользователь:** @{callback_query.from_user.username or 'без username'}\n"
            f"**Имя:** {callback_query.from_user.first_name}\n"
            f"**ID:** {callback_query.from_user.id}\n"
            f"**План:** {order.subscription_plan.name}\n"
            f"**Сумма:** {order.total_amount}₽\n"
            f"**Spotify логин:** {order.spotify_login}\n\n"
            f"🔗 **Ссылка на оплату:** {order.payment_url}"
        )
        
        await callback_query.bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления администратору: {e}")
    
    await state.clear()
    await callback_query.answer()

async def process_start_over(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Начать заново'"""
    await state.clear()
    await cmd_start(callback_query.message, state)
    await callback_query.answer()

async def handle_unknown_message(message: types.Message):
    """Обработчик неизвестных сообщений"""
    unknown_text = (
        "❓ Я не понимаю эту команду.\n\n"
        "Используйте кнопки меню для навигации или введите /start для перезапуска бота."
    )
    
    keyboard = get_back_to_start_keyboard()
    await message.answer(unknown_text, reply_markup=keyboard)

async def cmd_admin_orders(message: types.Message):
    """Команда для просмотра заказов (только для админов)"""
    if message.from_user.id != ADMIN_ID:
        return
    
    with app.app_context():
        orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
        
        if not orders:
            await message.answer("📋 Нет заказов")
            return
        
        orders_text = "📋 **Последние 10 заказов:**\n\n"
        
        for order in orders:
            orders_text += (
                f"**{order.id}**\n"
                f"├ Пользователь: {order.user.first_name} (@{order.user.username or 'без username'})\n"
                f"├ План: {order.subscription_plan.name}\n"
                f"├ Сумма: {order.total_amount}₽\n"
                f"├ Статус: {order.status.value}\n"
                f"└ Создан: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            )
        
        await message.answer(orders_text, parse_mode="Markdown")
