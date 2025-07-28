import os
import logging

# Конфигурация бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "demo_mode")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # ID администратора для уведомлений

# Конфигурация базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/spotify_bot")

# Digiseller API конфигурация
DIGISELLER_SELLER_ID = os.getenv("DIGISELLER_SELLER_ID", "")
DIGISELLER_SECRET_KEY = os.getenv("DIGISELLER_SECRET_KEY", "")
DIGISELLER_API_URL = "https://shop.digiseller.ru/xml"

# Webhook конфигурация
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://your-domain.com")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Варианты подписок
SUBSCRIPTION_PLANS = {
    "1_month": {
        "name": "1 месяц",
        "price": 150,
        "duration": "1 месяц"
    },
    "3_months": {
        "name": "3 месяца", 
        "price": 370,
        "duration": "3 месяца"
    },
    "6_months": {
        "name": "6 месяцев",
        "price": 690,
        "duration": "6 месяцев"
    },
    "12_months": {
        "name": "12 месяцев",
        "price": 1300,
        "duration": "12 месяцев"
    }
}

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
