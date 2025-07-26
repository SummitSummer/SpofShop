import logging

try:
    import ssl
except ModuleNotFoundError:
    print("\n❌ Ошибка: отсутствует модуль `ssl`, необходимый для HTTPS-соединений.")
    print("Пожалуйста, запустите этот скрипт в окружении, где доступен модуль `ssl`, например Render.com или локальный Python с OpenSSL.")
    exit(1)

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# === Настройки бота ===
API_TOKEN = '8361282581:AAHALZB4M1vuPU5-BTyJSzarG2Z7YASa9J4'
ADMIN_ID = 2137078270

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# === Клавиатура с вариантами подписок ===
kb_subscriptions = ReplyKeyboardMarkup(resize_keyboard=True)
kb_subscriptions.add(
    KeyboardButton('1 месяц - 150₽'),
    KeyboardButton('3 месяца - 370₽')
)
kb_subscriptions.add(
    KeyboardButton('6 месяцев - 690₽'),
    KeyboardButton('12 месяцев - 1300₽')
)

# === Временное хранилище данных пользователя ===
user_data = {}

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        "👋 Привет!\n\n"
        "Добро пожаловать в магазин Spotify Family.\n"
        "Выбери подходящий срок подписки:",
        reply_markup=kb_subscriptions
    )

@dp.message_handler(lambda message: message.text.startswith(('1 месяц', '3 месяца', '6 месяцев', '12 месяцев')))
async def handle_subscription_choice(message: types.Message):
    user_data[message.from_user.id] = {
        'subscription': message.text
    }
    await message.answer("✉️ Введи логин или почту от Spotify, которую нужно добавить в семью:")

@dp.message_handler(lambda message: message.from_user.id in user_data and 'login' not in user_data[message.from_user.id])
async def handle_spotify_login(message: types.Message):
    user_data[message.from_user.id]['login'] = message.text

    subscription = user_data[message.from_user.id]['subscription']
    login = user_data[message.from_user.id]['login']
    tg_username = message.from_user.username or 'без ника'

    # Сообщение клиенту (без ссылки оплаты)
    await message.answer(
        "✅ Спасибо за заказ!\n\n"
        "Ожидайте подтверждения от менеджера."
    )

    # Уведомление админу
    admin_msg = (
        f"\ud83d\udd14 Новый заказ:\n"
        f"Подписка: {subscription}\n"
        f"Spotify логин: {login}\n"
        f"Telegram: @{tg_username}"
    )
    await bot.send_message(ADMIN_ID, admin_msg)

    # Очистка временных данных
    del user_data[message.from_user.id]

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
