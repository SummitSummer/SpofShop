# Telegram Bot for Spotify Family Subscriptions

## Overview

This is a Telegram bot built with aiogram 3.x that facilitates the sale of Spotify Family subscriptions. The bot guides users through a multi-step process: subscription plan selection, Spotify login entry, payment processing, and order completion. It uses finite state machines for conversation flow management and includes basic order tracking functionality.

**Status**: ✅ Fully operational and deployed
**Last Updated**: 2025-07-27

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The bot follows a modular architecture with clear separation of concerns:

- **Bot Framework**: aiogram 3.21.0 (async Telegram bot framework)
- **State Management**: FSM (Finite State Machine) with memory storage
- **Data Storage**: In-memory storage for orders (no persistent database)
- **Configuration**: Environment-based configuration management via Replit Secrets
- **Logging**: File and console logging with structured format

## Recent Changes (2025-07-27)

✅ **Major Architecture Update**:
- Migrated from aiogram 2.x to aiogram 3.21.0
- Updated all imports and API calls for new framework version
- Fixed inline keyboard creation using new syntax
- Updated FSM state management methods
- Implemented F-filter system for callback handling
- Added proper null-safety checks for user data

✅ **Deployment Configuration**:
- Configured environment variables via Replit Secrets (BOT_TOKEN, ADMIN_ID)
- Bot successfully deployed and operational
- Verified all core functionality working correctly

✅ **UI/UX Improvements**:
- Added main menu with 3 buttons: 🎟 Оформить подписку, 💬 Support, 📖 FAQ
- Enhanced subscription selection with emoji styling (💚) and Pikachu+Spotify image
- Updated Spotify credentials input to require login:password format
- Added comprehensive FAQ with 8 questions corrected for password requirement
- Implemented support contact integration (https://t.me/chanceofrain)
- Added back navigation buttons throughout the interface
- Enhanced payment interface with step-by-step instructions
- Improved text formatting with Markdown support
- Added input validation for login:password format

## Key Components

### 1. Bot Entry Point (`bot.py`)
- Initializes the bot and dispatcher
- Sets up logging configuration
- Registers message and callback handlers
- Uses MemoryStorage for FSM state persistence

### 2. Handlers (`handlers.py`)
- **cmd_start**: Initiates the subscription selection process
- **process_plan_selection**: Handles subscription plan choices
- **process_spotify_login**: Manages Spotify login input
- **process_payment_completed**: Processes payment confirmations
- **cmd_admin_orders**: Admin functionality for viewing orders

### 3. State Management (`states.py`)
- **OrderState**: Defines conversation states
  - choosing_subscription
  - entering_spotify_login
  - payment_processing
  - order_completed

### 4. User Interface (`keyboards.py`)
- **get_subscription_keyboard**: Creates plan selection buttons
- **get_payment_keyboard**: Generates payment and confirmation buttons
- **get_back_to_start_keyboard**: Provides restart functionality

### 5. Data Layer (`storage.py`)
- **OrderStorage**: In-memory order management
- Order creation with unique IDs
- Order status tracking and updates
- Simple counter-based ID generation

### 6. Configuration (`config.py`)
- Environment variable management
- Subscription plan definitions with pricing
- Admin user configuration
- Logging setup

## Data Flow

1. **User Initiation**: User sends /start command
2. **Order Creation**: System creates new order record in memory
3. **Plan Selection**: User chooses subscription duration and price
4. **Spotify Login**: User provides Spotify account details
5. **Payment Processing**: User completes external payment and confirms
6. **Order Completion**: System marks order as completed

## External Dependencies

- **aiogram**: Telegram Bot API framework
- **Python Standard Library**: logging, asyncio, os, json, datetime
- **Environment Variables**: BOT_TOKEN, ADMIN_ID

## Deployment Strategy

The current architecture uses:
- **Memory Storage**: All data stored in RAM (lost on restart)
- **File Logging**: bot.log file for persistent logs
- **Environment Configuration**: Runtime configuration via environment variables

### Limitations and Improvement Opportunities

1. **Data Persistence**: Orders are lost on bot restart due to memory-only storage
2. **Payment Integration**: No actual payment processor integration
3. **User Management**: No user authentication or session management
4. **Scalability**: Single-instance deployment with no horizontal scaling support

### Recommended Enhancements

1. **Database Integration**: Replace memory storage with persistent database (PostgreSQL recommended)
2. **Payment Gateway**: Integrate with payment processors (Stripe, PayPal, etc.)
3. **Admin Panel**: Web-based admin interface for order management
4. **Error Handling**: More robust error handling and user feedback
5. **Security**: Input validation and rate limiting implementation