# Spotify Subscription Bot

## Overview

This is a Telegram bot for selling Spotify Premium subscriptions with an integrated Flask web admin panel. The system handles user registration, subscription ordering, payment processing through Digiseller, and provides comprehensive administrative tools for managing orders, users, and system settings.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Flask Web Application**: Serves the admin panel and handles webhooks
- **Telegram Bot**: Built with aiogram for asynchronous message handling
- **Database Layer**: SQLAlchemy ORM with Flask-SQLAlchemy for data management
- **Payment Processing**: Digiseller API integration for payment handling

### Frontend Architecture
- **Admin Panel**: Server-side rendered HTML templates with Bootstrap 5
- **Spotify Theme**: Custom CSS styling matching Spotify's brand colors
- **Interactive Dashboard**: JavaScript-enhanced admin interface with real-time updates

## Key Components

### Database Models
- **User**: Stores Telegram user information and activity tracking
- **Order**: Manages subscription orders with status tracking
- **Payment**: Handles payment records and transaction data
- **SubscriptionPlan**: Defines available subscription tiers and pricing
- **Admin**: Administrative user accounts for web panel access
- **BroadcastMessage**: System for mass messaging users

### Bot Handlers
- **Command Handlers**: `/start` command and admin-specific commands
- **Callback Handlers**: Interactive keyboard button responses
- **State Management**: FSM (Finite State Machine) for order flow
- **User Registration**: Automatic user creation and data updates

### Payment System
- **Digiseller Integration**: Third-party payment processor for RUB transactions
- **Webhook Processing**: Automatic payment confirmation handling
- **Order Status Updates**: Real-time status changes based on payment events

### Admin Panel Features
- **Dashboard**: Statistics and system overview
- **User Management**: User listing, search, and moderation tools
- **Order Management**: Order tracking and status updates
- **Payment Tracking**: Payment history and transaction monitoring
- **Mass Broadcasting**: System for sending messages to all users
- **System Settings**: Configurable bot behavior and messages

## Data Flow

### Order Process
1. User starts conversation with `/start` command
2. Bot displays main menu with subscription options
3. User selects subscription plan
4. System creates order record in database
5. Payment URL generated through Digiseller API
6. User completes payment on external platform
7. Digiseller sends webhook notification
8. System updates order and payment status
9. Admin receives notification for manual processing

### User Management
1. Automatic user registration on first interaction
2. User data updates on subsequent interactions
3. Activity tracking for engagement analytics
4. Admin tools for user moderation and support

## External Dependencies

### Required Services
- **Telegram Bot API**: Core bot functionality
- **PostgreSQL Database**: Data persistence (configured automatically)

### Environment Variables
- `BOT_TOKEN`: Telegram bot authentication token (Required for bot functionality)
- `ADMIN_ID`: Telegram user ID for admin notifications (Optional)
- `DATABASE_URL`: Database connection string (Set automatically)
- `SESSION_SECRET`: Flask session encryption key (Set automatically)

### Optional Payment System (Disabled in current setup)
- `DIGISELLER_SELLER_ID`: Payment gateway merchant ID
- `DIGISELLER_SECRET_KEY`: Payment gateway API key
- `WEBHOOK_HOST`: Public domain for webhook endpoints

### Python Dependencies
- **Flask**: Web framework for admin panel
- **aiogram**: Asynchronous Telegram bot framework
- **SQLAlchemy**: Database ORM
- **requests**: HTTP client for API calls
- **werkzeug**: WSGI utilities and security helpers

## Deployment Strategy

### Development Setup
- Flask development server on port 5000
- SQLite database for local testing
- Polling mode for Telegram bot (no webhooks required)

### Production Considerations
- **Database**: PostgreSQL with connection pooling
- **Web Server**: WSGI server (Gunicorn recommended)
- **SSL/TLS**: Required for webhook endpoints
- **Environment Variables**: Secure configuration management
- **Logging**: Structured logging for monitoring and debugging

### File Structure
- `app.py`: Flask application initialization
- `main.py`: Flask application entry point
- `start_bot.py`: Telegram bot startup script
- `bot_handlers.py`: Telegram bot message handlers and logic
- `models.py`: Database schema definitions
- `routes.py`: Flask web routes for admin panel
- `config.py`: Configuration and environment variables
- `templates/`: HTML templates for admin interface
- `static/`: CSS, JavaScript, and image assets
- `run_bot.sh`: Shell script for easy bot startup

### Current Status (Updated)
- ✅ Flask admin panel fully functional
- ✅ PostgreSQL database configured
- ✅ Authentication system working (admin/admin123)
- ✅ Demo data generation available
- ⚠️ Telegram bot requires BOT_TOKEN to be set
- ❌ Payment system disabled (can be enabled later)