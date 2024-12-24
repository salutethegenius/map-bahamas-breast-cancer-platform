
import io
import csv
import os
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy.orm import DeclarativeBase
import logging
from sqlalchemy import event
from sqlalchemy.exc import OperationalError
from time import sleep

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.debug = True

# Configuration
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

# Initialize extensions
db = SQLAlchemy(model_class=Base)
mail = Mail(app)
login_manager = LoginManager()

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

from models import Company, User

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def initialize_database():
    with app.app_context():
        @event.listens_for(db.engine, 'connect')
        def connect(dbapi_connection, connection_record):
            logger.info("Database connection established")

        @event.listens_for(db.engine, 'disconnect')
        def disconnect(dbapi_connection, connection_record):
            logger.info("Database connection closed")

        db.create_all()
        
        # Create admin user if not exists
        admin_user = User.query.filter_by(email='admin@mapbahamas.com').first()
        if not admin_user:
            admin = User(email='admin@mapbahamas.com', is_admin=True)
            admin.set_password('adminpass123')
            db.session.add(admin)
            db.session.commit()

# Initialize database
initialize_database()

# [Rest of your routes and application code remains the same]
[Previous route definitions and application code]
