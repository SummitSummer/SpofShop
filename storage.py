"""
Database storage using SQLAlchemy models
This file is kept for compatibility but functionality moved to models.py
"""

from models import User, Order, SubscriptionPlan, Payment, BroadcastMessage, db
from app import app
import logging

logger = logging.getLogger(__name__)

class DatabaseStorage:
    """Database storage for orders and users using SQLAlchemy"""
    
    @staticmethod
    def create_user(telegram_user):
        """Create or update user in database"""
        with app.app_context():
            user = User.query.filter_by(id=telegram_user.id).first()
            if not user:
                user = User()
                user.id = telegram_user.id
                user.username = telegram_user.username
                user.first_name = telegram_user.first_name
                user.last_name = telegram_user.last_name
                user.language_code = telegram_user.language_code
                db.session.add(user)
            else:
                user.username = telegram_user.username
                user.first_name = telegram_user.first_name
                user.last_name = telegram_user.last_name
            
            db.session.commit()
            return user
    
    @staticmethod
    def create_order(user_id, plan_id, total_amount):
        """Create new order"""
        with app.app_context():
            order_count = Order.query.count() + 1
            order_id = f"ORDER_{order_count:05d}"
            
            order = Order()
            order.id = order_id
            order.user_id = user_id
            order.plan_id = plan_id
            order.total_amount = total_amount
            db.session.add(order)
            db.session.commit()
            return order
    
    @staticmethod
    def get_order(order_id):
        """Get order by ID"""
        with app.app_context():
            return Order.query.filter_by(id=order_id).first()
    
    @staticmethod
    def update_order(order_id, **kwargs):
        """Update order"""
        with app.app_context():
            order = Order.query.filter_by(id=order_id).first()
            if order:
                for key, value in kwargs.items():
                    setattr(order, key, value)
                db.session.commit()
            return order
    
    @staticmethod
    def get_user_orders(user_id):
        """Get all orders for user"""
        with app.app_context():
            return Order.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_all_orders():
        """Get all orders"""
        with app.app_context():
            return Order.query.order_by(Order.created_at.desc()).all()

# Global storage instance
storage = DatabaseStorage()
