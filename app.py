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

# Database configuration
def get_database_url():
    """Get and format database URL"""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL environment variable is not set")
        raise RuntimeError("Database configuration is missing")

    # If using postgres:// convert to postgresql://
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    elif db_url.startswith('https://'):
        # Extract the relevant parts from the URL
        db_url = f"postgresql://{os.environ.get('PGUSER')}:{os.environ.get('PGPASSWORD')}@{os.environ.get('PGHOST')}:{os.environ.get('PGPORT')}/{os.environ.get('PGDATABASE')}"

    logger.info(f"Using database type: {db_url.split('://')[0]}")
    return db_url

# Configure SQLAlchemy with improved connection handling
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,  # Enable pessimistic connection testing
    "pool_recycle": 300,    # Recycle connections every 5 minutes
    "pool_timeout": 20,     # Connection timeout after 20 seconds
    "max_overflow": 5,      # Allow up to 5 connections beyond pool size
    "connect_args": {
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    },
}

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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
        retry_count = 0
        max_retries = 3
        retry_delay = 2

        while retry_count < max_retries:
            try:
                logger.info("Creating database tables...")
                db.create_all()

                # Create admin user if not exists
                admin_user = User.query.filter_by(email='admin@mapbahamas.com').first()
                if not admin_user:
                    logger.info("Creating admin user...")
                    admin = User(email='admin@mapbahamas.com', is_admin=True)
                    admin.set_password('adminpass123')
                    db.session.add(admin)
                    db.session.commit()
                    logger.info("Admin user created successfully")
                else:
                    # Update existing admin password if needed
                    admin_user.set_password('adminpass123')
                    db.session.commit()
                    logger.info("Admin user password updated")
                return True

            except OperationalError as e:
                retry_count += 1
                logger.warning(f"Database connection attempt {retry_count} failed: {str(e)}")
                if retry_count < max_retries:
                    sleep(retry_delay)
                else:
                    logger.error("Maximum retries reached. Could not connect to database.")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error during database initialization: {str(e)}")
                raise

# Only initialize database when running directly
if __name__ == '__main__':
    initialize_database()