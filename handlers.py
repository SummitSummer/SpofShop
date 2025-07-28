import logging
from aiogram import types
from aiogram.fsm.context import FSMContext

from config import SUBSCRIPTION_PLANS, ADMIN_ID
from states import OrderState
from keyboards import (
    get_main_menu_keyboard, get_subscription_keyboard, get_payment_keyboard, 
    get_back_to_start_keyboard, get_back_to_menu_keyboard
)
from storage import order_storage

logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start - показывает главное меню с изображением"""
    # Очищаем предыдущие состояния
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
    user_id = callback_query.from_user.id if callback_query.from_user else 0
    user_data = {
        "username": callback_query.from_user.username if callback_query.from_user else None,
        "first_name": callback_query.from_user.first_name if callback_query.from_user else None
    }
    order_storage.create_order(user_id, user_data)
    
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
    
    if plan_id not in SUBSCRIPTION_PLANS:
        await callback_query.answer("❌ Неверный план подписки")
        return
    
    plan_info = SUBSCRIPTION_PLANS[plan_id]
    
    # Сохраняем выбранный план
    await state.update_data(selected_plan=plan_id)
    user_id = callback_query.from_user.id if callback_query.from_user else 0
    order_storage.update_order(
        user_id,
        subscription_plan=plan_info
    )
    
    # Запрашиваем логин от Spotify с подробными инструкциями
    text = (
        f"✅ **Выбрана подписка:** {plan_info['name']} — {plan_info['price']}₽\n\n"
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
    
    # Сохраняем логин
    await state.update_data(spotify_login=spotify_login)
    user_id = message.from_user.id if message.from_user else 0
    order_storage.update_order(
        user_id,
        spotify_login=spotify_login
    )
    
    # Генерируем фиктивную ссылку на оплату
    state_data = await state.get_data()
    plan_id = state_data.get("selected_plan")
    if not plan_id or plan_id not in SUBSCRIPTION_PLANS:
        return
        
    plan_info = SUBSCRIPTION_PLANS[plan_id]
    
    # Фиктивная ссылка на оплату
    payment_url = f"https://payment-gateway.example.com/pay?order_id={state_data.get('order_id')}&amount={plan_info['price']}"
    
    await state.update_data(payment_url=payment_url)
    user_id = message.from_user.id if message.from_user else 0
    order_storage.update_order(
        user_id,
        payment_url=payment_url,
        status="awaiting_payment"
    )
    
    # Отправляем сообщение с оплатой
    payment_text = (
        f"💳 **К оплате:** {plan_info['price']}₽\n\n"
        f"📋 **Детали заказа:**\n"
        f"• **Подписка:** {plan_info['name']}\n"
        f"• **Spotify аккаунт:** {spotify_login}\n\n"
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
    user_id = callback_query.from_user.id if callback_query.from_user else 0
    order = order_storage.get_order(user_id)
    
    if not order:
        await callback_query.answer("❌ Заказ не найден")
        return
    
    # Завершаем заказ
    order_storage.complete_order(user_id)
    
    # Уведомляем пользователя
    success_text = (
        "✅ Оплата успешно обработана!\n\n"
        "📞 Администратор свяжется с вами в ближайшее время для активации подписки.\n"
        "Обычно это занимает до 24 часов."
    )
    
    if callback_query.message:
        await callback_query.message.edit_text(success_text, reply_markup=get_back_to_start_keyboard())
    
    # Уведомляем администратора
    if callback_query.bot:
        await notify_admin_about_order(callback_query.bot, order)
    
    await state.set_state(OrderState.order_completed)
    await callback_query.answer("✅ Оплата подтверждена!")

async def notify_admin_about_order(bot, order):
    """Отправляет уведомление администратору о новом заказе"""
    try:
        admin_text = (
            "🔔 Новый оплаченный заказ:\n\n"
            f"📋 ID заказа: {order['order_id']}\n"
            f"📅 Подписка: {order['subscription_plan']['name']} - {order['subscription_plan']['price']}₽\n"
            f"📧 Spotify логин: {order['spotify_login']}\n"
            f"👤 Пользователь: {order['first_name']}\n"
            f"📱 Telegram: @{order['username'] or 'не указан'}\n"
            f"🆔 User ID: {order['user_id']}\n"
            f"⏰ Время заказа: {order['created_at']}"
        )
        
        await bot.send_message(ADMIN_ID, admin_text)
        logger.info(f"Уведомление администратору отправлено для заказа {order['order_id']}")
        
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления администратору: {e}")

async def process_start_over(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Начать заново'"""
    await state.clear()
    
    # Создаем новое сообщение как /start
    if callback_query.message:
        await cmd_start(callback_query.message, state)
    await callback_query.answer()

async def handle_unknown_message(message: types.Message, state: FSMContext):
    """Обработка неизвестных сообщений в состояниях"""
    current_state = await state.get_state()
    
    if current_state == OrderState.choosing_subscription:
        await message.answer(
            "Пожалуйста, выберите план подписки, используя кнопки выше.",
            reply_markup=get_back_to_start_keyboard()
        )
    elif current_state == OrderState.entering_spotify_login:
        await message.answer(
            "Пожалуйста, введите ваш логин/почту от Spotify:",
            reply_markup=get_back_to_start_keyboard()
        )
    elif current_state == OrderState.payment_processing:
        await message.answer(
            "Пожалуйста, используйте кнопки для оплаты выше.",
            reply_markup=get_back_to_start_keyboard()
        )
    else:
        await message.answer(
            "Для начала работы с ботом нажмите /start",
            reply_markup=get_back_to_start_keyboard()
        )

# Команда для администратора для просмотра заказов
async def cmd_admin_orders(message: types.Message):
    """Команда для администратора для просмотра всех заказов"""
    user_id = message.from_user.id if message.from_user else 0
    if str(user_id) != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    orders = order_storage.get_all_orders()
    
    if not orders:
        await message.answer("📋 Заказов пока нет.")
        return
    
    response_parts = ["📋 Все заказы:\n"]
    
    for user_id, order in orders.items():
        order_info = (
            f"\n🆔 {order['order_id']}\n"
            f"👤 {order['first_name']} (@{order.get('username', 'не указан')})\n"
            f"📧 {order.get('spotify_login', 'не указан')}\n"
            f"📅 {order.get('subscription_plan', {}).get('name', 'не выбрано')}\n"
            f"💰 {order.get('subscription_plan', {}).get('price', 0)}₽\n"
            f"📊 Статус: {order['status']}\n"
            f"⏰ {order['created_at']}\n"
            "─────────────────"
        )
        response_parts.append(order_info)
    
    # Разбиваем на части если слишком длинное сообщение
    full_response = "\n".join(response_parts)
    
    if len(full_response) > 4000:
        # Отправляем по частям
        current_message = response_parts[0]
        for part in response_parts[1:]:
            if len(current_message + part) > 4000:
                await message.answer(current_message)
                current_message = part
            else:
                current_message += part
        
        if current_message:
            await message.answer(current_message)
    else:
        await message.answer(full_response)
