import os
import logging

# Конфигурация бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
ADMIN_ID = os.getenv("ADMIN_ID", "123456789")  # ID администратора для уведомлений

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
