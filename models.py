from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Text, JSON
import enum

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"

class OrderStatus(enum.Enum):
    CREATED = "created"
    AWAITING_PAYMENT = "awaiting_payment"
    PAID = "paid"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.BigInteger, primary_key=True)  # Telegram user ID
    username = db.Column(db.String(255), nullable=True)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    language_code = db.Column(db.String(10), default='ru')
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    is_active = db.Column(db.Boolean, default=True)
    is_banned = db.Column(db.Boolean, default=False)
    ban_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.id}: {self.username or self.first_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'language_code': self.language_code,
            'role': self.role.value if self.role else None,
            'is_active': self.is_active,
            'is_banned': self.is_banned,
            'ban_reason': self.ban_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Admin {self.username}>'

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.String(50), primary_key=True)  # e.g., '1_month', '3_months'
    name = db.Column(db.String(100), nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)  # Price in rubles
    is_active = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='subscription_plan', lazy=True)
    
    def __repr__(self):
        return f'<SubscriptionPlan {self.name}: {self.price}₽>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'duration_months': self.duration_months,
            'price': self.price,
            'is_active': self.is_active,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.String(50), primary_key=True)  # ORDER_00001 format
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.String(50), db.ForeignKey('subscription_plans.id'), nullable=False)
    spotify_login = db.Column(db.String(255), nullable=True)
    spotify_password = db.Column(db.String(255), nullable=True)  # Encrypted
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.CREATED)
    total_amount = db.Column(db.Integer, nullable=False)  # Price in rubles
    payment_url = db.Column(db.String(500), nullable=True)
    digiseller_order_id = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    payments = db.relationship('Payment', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id}: {self.status.value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'spotify_login': self.spotify_login,
            'status': self.status.value if self.status else None,
            'total_amount': self.total_amount,
            'payment_url': self.payment_url,
            'digiseller_order_id': self.digiseller_order_id,
            'notes': self.notes,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'user': self.user.to_dict() if self.user else None,
            'subscription_plan': self.subscription_plan.to_dict() if self.subscription_plan else None
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Amount in rubles
    currency = db.Column(db.String(10), default='RUB')
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = db.Column(db.String(50), default='digiseller')
    external_payment_id = db.Column(db.String(100), nullable=True)  # Digiseller payment ID
    payment_data = db.Column(JSON, nullable=True)  # Additional payment data
    paid_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.id}: {self.amount}₽ - {self.status.value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status.value if self.status else None,
            'payment_method': self.payment_method,
            'external_payment_id': self.external_payment_id,
            'payment_data': self.payment_data,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BroadcastMessage(db.Model):
    __tablename__ = 'broadcast_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    target_users = db.Column(JSON, nullable=True)  # List of user IDs or filters
    sent_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='draft')  # draft, sending, completed, failed
    created_by = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
    
    admin = db.relationship('Admin', backref='broadcast_messages')
    
    def __repr__(self):
        return f'<BroadcastMessage {self.title}: {self.status}>'

class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemSettings {self.key}: {self.value}>'

# Initialize default subscription plans
def init_default_data():
    """Initialize default subscription plans and admin user"""
    with db.session.begin():
        # Create default subscription plans
        plans_data = [
            {"id": "1_month", "name": "1 месяц", "duration_months": 1, "price": 150},
            {"id": "3_months", "name": "3 месяца", "duration_months": 3, "price": 370},
            {"id": "6_months", "name": "6 месяцев", "duration_months": 6, "price": 690},
            {"id": "12_months", "name": "12 месяцев", "duration_months": 12, "price": 1300},
        ]
        
        plans = []
        for plan_data in plans_data:
            plan = SubscriptionPlan()
            for key, value in plan_data.items():
                setattr(plan, key, value)
            plans.append(plan)
        
        for plan in plans:
            existing = SubscriptionPlan.query.filter_by(id=plan.id).first()
            if not existing:
                db.session.add(plan)
        
        # Create default admin user
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin()
            admin.username = 'admin'
            admin.email = 'admin@spotify-bot.com'
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Create default system settings
        settings_data = [
            {'key': 'bot_welcome_message', 'value': '🎵 Добро пожаловать в Spotify Family Bot! 🎵', 'description': 'Приветственное сообщение бота'},
            {'key': 'digiseller_seller_id', 'value': '', 'description': 'ID продавца в Digiseller'},
            {'key': 'digiseller_secret_key', 'value': '', 'description': 'Секретный ключ Digiseller'},
            {'key': 'support_username', 'value': 'chanceofrain', 'description': 'Username для поддержки'},
        ]
        
        settings = []
        for setting_data in settings_data:
            setting = SystemSettings()
            for key, value in setting_data.items():
                setattr(setting, key, value)
            settings.append(setting)
        
        for setting in settings:
            existing = SystemSettings.query.filter_by(key=setting.key).first()
            if not existing:
                db.session.add(setting)
