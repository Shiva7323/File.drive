from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or "dev-secret-key-change-in-production"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) # needed for url_for to generate with https

# Database configuration
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    # Use SQLite for local development if no DATABASE_URL is set
    database_url = "sqlite:///app.db"
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app, model_class=Base)

# Create tables
with app.app_context():
    import models  # noqa: F401
    import auth  # noqa: F401
    db.create_all()
    logging.info("Database tables created")
