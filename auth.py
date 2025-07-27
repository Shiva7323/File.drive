import uuid
from functools import wraps
from flask import g, session, redirect, request, render_template, url_for, flash
from flask_login import LoginManager, login_user, logout_user, current_user
from werkzeug.local import LocalProxy

from app import app, db
from models import User

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            session["next_url"] = get_next_navigation_url(request)
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_next_navigation_url(request):
    is_navigation_url = request.headers.get('Sec-Fetch-Mode') == 'navigate' and request.headers.get('Sec-Fetch-Dest') == 'document'
    if is_navigation_url:
        return request.url
    return request.referrer or request.url 