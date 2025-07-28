#!/usr/bin/env python3
"""
Startup script for Telegram bot
"""
import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app import app
from models import init_default_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Main bot startup function"""
    # Get bot token from environment
    bot_token = os.getenv("BOT_TOKEN")
    
    if not bot_token or bot_token == "demo_mode":
        logger.error("BOT_TOKEN environment variable not set or in demo mode")
        logger.info("Please set BOT_TOKEN environment variable with your bot token from @BotFather")
        sys.exit(1)
    
    # Initialize database
    with app.app_context():
        init_default_data()
        logger.info("Database initialized")
    
    # Create bot and dispatcher
    bot = Bot(token=bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Import and register handlers
    from bot_handlers import register_handlers
    register_handlers(dp)
    
    logger.info("Bot handlers registered")
    
    # Start polling
    try:
        logger.info("Starting bot polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)