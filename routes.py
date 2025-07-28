from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash
from app import app, db
from models import Admin, User, Order, SubscriptionPlan, Payment, BroadcastMessage, SystemSettings, OrderStatus, PaymentStatus
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import json

def login_required(f):
    """Decorator for requiring admin login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
def admin_redirect():
    """Redirect /admin to /admin/login"""
    return redirect(url_for('login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter(
            (Admin.username == username) | (Admin.email == username)
        ).first()
        
        if admin and admin.check_password(password) and admin.is_active:
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            admin.last_login = datetime.utcnow()
            db.session.commit()
            flash('Успешный вход в систему', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверный логин или пароль', 'error')
    
    return render_template('login.html')

@app.route('/admin/logout')
def logout():
    """Admin logout"""
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@login_required
def dashboard():
    """Admin dashboard with statistics"""
    # Get statistics
    total_users = User.query.count()
    total_orders = Order.query.count()
    completed_orders = Order.query.filter_by(status=OrderStatus.COMPLETED).count()
    total_revenue = db.session.query(func.sum(Payment.amount)).filter_by(status=PaymentStatus.COMPLETED).scalar() or 0
    
    # Get recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    # Get monthly statistics
    today = datetime.utcnow()
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_orders = Order.query.filter(Order.created_at >= month_start).count()
    monthly_revenue = db.session.query(func.sum(Payment.amount)).filter(
        and_(Payment.created_at >= month_start, Payment.status == PaymentStatus.COMPLETED)
    ).scalar() or 0
    
    # Get daily statistics for chart (last 30 days)
    daily_stats = []
    for i in range(30):
        day = today - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        orders_count = Order.query.filter(
            and_(Order.created_at >= day_start, Order.created_at < day_end)
        ).count()
        
        revenue = db.session.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.created_at >= day_start,
                Payment.created_at < day_end,
                Payment.status == PaymentStatus.COMPLETED
            )
        ).scalar() or 0
        
        daily_stats.append({
            'date': day.strftime('%Y-%m-%d'),
            'orders': orders_count,
            'revenue': revenue
        })
    
    daily_stats.reverse()
    
    return render_template('dashboard.html', 
                         total_users=total_users,
                         total_orders=total_orders,
                         completed_orders=completed_orders,
                         total_revenue=total_revenue,
                         monthly_orders=monthly_orders,
                         monthly_revenue=monthly_revenue,
                         recent_orders=recent_orders,
                         daily_stats=json.dumps(daily_stats))

@app.route('/admin/users')
@login_required
def users():
    """Users management page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.first_name.contains(search)) |
            (User.last_name.contains(search))
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('users.html', users=users, search=search)

@app.route('/admin/orders')
@login_required
def orders():
    """Orders management page"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = Order.query
    
    if status_filter:
        query = query.filter(Order.status == OrderStatus(status_filter))
    
    if search:
        query = query.join(User).filter(
            (Order.id.contains(search)) |
            (User.username.contains(search)) |
            (User.first_name.contains(search))
        )
    
    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('orders.html', orders=orders, 
                         status_filter=status_filter, search=search,
                         order_statuses=OrderStatus)

@app.route('/admin/payments')
@login_required
def payments():
    """Payments management page"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Payment.query
    
    if status_filter:
        query = query.filter(Payment.status == PaymentStatus(status_filter))
    
    payments = query.order_by(Payment.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('payments.html', payments=payments,
                         status_filter=status_filter,
                         payment_statuses=PaymentStatus)

@app.route('/admin/broadcast', methods=['GET', 'POST'])
@login_required
def broadcast():
    """Mass broadcast page"""
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        target_filter = request.form.get('target_filter', 'all')
        
        # Create broadcast message
        broadcast_msg = BroadcastMessage()
        broadcast_msg.title = title
        broadcast_msg.message = message
        broadcast_msg.target_users = {'filter': target_filter}
        broadcast_msg.created_by = session['admin_id']
        db.session.add(broadcast_msg)
        db.session.commit()
        
        flash(f'Рассылка "{title}" создана и будет отправлена', 'success')
        return redirect(url_for('broadcast'))
    
    # Get broadcast history
    broadcasts = BroadcastMessage.query.order_by(BroadcastMessage.created_at.desc()).limit(20).all()
    
    # Get user statistics for targeting
    total_users = User.query.filter_by(is_active=True).count()
    active_users = User.query.filter(
        and_(User.is_active == True, User.last_activity >= datetime.utcnow() - timedelta(days=7))
    ).count()
    
    return render_template('broadcast.html', broadcasts=broadcasts,
                         total_users=total_users, active_users=active_users)

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """System settings page"""
    if request.method == 'POST':
        # Handle bot start/stop
        if 'start_demo_bot' in request.form:
            from bot_runner import start_demo_bot
            result = start_demo_bot()
            flash(result, 'success')
            return redirect(url_for('settings'))
        
        if 'stop_demo_bot' in request.form:
            from bot_runner import stop_demo_bot
            stop_demo_bot()
            flash('Демо-бот остановлен', 'info')
            return redirect(url_for('settings'))
            
        if 'check_bot_token' in request.form:
            import os
            bot_token = os.getenv("BOT_TOKEN", "demo_mode")
            if bot_token != "demo_mode" and bot_token:
                flash(f'Токен бота настроен: {bot_token[:10]}...', 'success')
            else:
                flash('Токен бота не настроен. Требуется BOT_TOKEN в переменных окружения.', 'error')
            return redirect(url_for('settings'))
        
        # Update settings
        for key, value in request.form.items():
            if key.startswith('setting_'):
                setting_key = key.replace('setting_', '')
                setting = SystemSettings.query.filter_by(key=setting_key).first()
                if setting:
                    setting.value = value
                    setting.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Настройки сохранены', 'success')
        return redirect(url_for('settings'))
    
    # Get all settings
    settings = SystemSettings.query.all()
    settings_dict = {s.key: s for s in settings}
    
    # Get subscription plans
    plans = SubscriptionPlan.query.all()
    
    return render_template('settings.html', settings=settings_dict, plans=plans)

# API endpoints for AJAX requests
@app.route('/api/user/<int:user_id>/ban', methods=['POST'])
@login_required
def ban_user(user_id):
    """Ban/unban user"""
    user = User.query.get_or_404(user_id)
    action = request.json.get('action')
    reason = request.json.get('reason', '')
    
    if action == 'ban':
        user.is_banned = True
        user.ban_reason = reason
        message = f'Пользователь {user.first_name} заблокирован'
    else:
        user.is_banned = False
        user.ban_reason = None
        message = f'Пользователь {user.first_name} разблокирован'
    
    db.session.commit()
    return jsonify({'success': True, 'message': message})

@app.route('/api/order/<order_id>/status', methods=['POST'])
@login_required
def update_order_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    new_status = request.json.get('status')
    admin_notes = request.json.get('notes', '')
    
    try:
        order.status = OrderStatus(new_status)
        order.admin_notes = admin_notes
        
        if new_status == 'completed':
            order.completed_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'Статус заказа обновлен на {new_status}'})
    except ValueError:
        return jsonify({'success': False, 'message': 'Неверный статус заказа'}), 400

@app.route('/api/stats/chart')
@login_required
def stats_chart():
    """Get chart data for dashboard"""
    days = request.args.get('days', 30, type=int)
    today = datetime.utcnow()
    
    chart_data = []
    for i in range(days):
        day = today - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        orders_count = Order.query.filter(
            and_(Order.created_at >= day_start, Order.created_at < day_end)
        ).count()
        
        revenue = db.session.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.created_at >= day_start,
                Payment.created_at < day_end,
                Payment.status == PaymentStatus.COMPLETED
            )
        ).scalar() or 0
        
        chart_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'orders': orders_count,
            'revenue': revenue
        })
    
    chart_data.reverse()
    return jsonify(chart_data)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
