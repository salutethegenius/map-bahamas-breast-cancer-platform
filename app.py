import io
import csv
import os
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, Response
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import logging
from sqlalchemy.exc import OperationalError
from time import sleep

from extensions import db
from forms import CompanyRegistrationForm, LoginForm # Added LoginForm import
from models import Company, User

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    # Handle different URL formats
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)

    # Ensure we're using the correct database URL format
    if not any(db_url.startswith(prefix) for prefix in ['postgresql://', 'postgres://']):
        logger.info("Constructing database URL from components...")
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
    "pool_size": 10,        # Set a reasonable pool size
    "connect_args": {
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    }
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
mail = Mail(app)
login_manager = LoginManager()

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def initialize_database():
    """Initialize database with retry mechanism"""
    with app.app_context():
        retry_count = 0
        max_retries = 3
        retry_delay = 2  # seconds

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
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    sleep(retry_delay)
                else:
                    logger.error("Maximum retries reached. Could not connect to database.")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error during database initialization: {str(e)}")
                raise

@app.route('/')
def index():
    package_stats = {
        'one_mile': Company.get_package_count('1mile'),
        'half_mile': Company.get_package_count('halfmile'),
        'quarter_mile': Company.get_package_count('quartermile'),
        'black_friday': Company.get_package_count('black_friday')
    }
    return render_template('index.html', package_stats=package_stats)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = CompanyRegistrationForm()
    if form.validate_on_submit():
        try:
            # Check Black Friday availability
            if form.package_tier.data == 'black_friday':
                available, remaining = Company.check_registration_availability('black_friday')
                if not available:
                    flash('Black Friday special is no longer available', 'error')
                    return redirect(url_for('register'))

            # Create new company
            company = Company(
                name=form.company_name.data,
                address=form.company_address.data,
                email=form.company_email.data,
                phone=form.company_phone.data,
                contact_name=form.contact_name.data,
                contact_email=form.contact_email.data,
                contact_phone=form.contact_phone.data,
                package_tier=form.package_tier.data,
                is_black_friday=(form.package_tier.data == 'black_friday')
            )

            # Handle contact photo
            if form.contact_photo.data:
                filename = secure_filename(form.contact_photo.data.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.contact_photo.data.save(filepath)
                company.contact_photo = os.path.join('uploads', filename)

            # Set payment date
            payment_date = request.form.get('payment_date')
            if payment_date:
                company.payment_date = datetime.strptime(payment_date, '%Y-%m-%d')

            db.session.add(company)
            db.session.commit()

            # Send confirmation email
            try:
                msg = Message('Registration Confirmation',
                            sender='noreply@mapbahamas.com',
                            recipients=[company.email])
                msg.body = f'Thank you for registering as a {company.package_tier} sponsor!'
                mail.send(msg)
            except Exception as e:
                logger.error(f"Failed to send confirmation email: {str(e)}")

            flash('Registration successful!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'error')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        flash('Invalid email or password', 'error')
    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))

    registrations = Company.query.all()
    package_stats = {
        'one_mile': Company.get_package_count('1mile'),
        'half_mile': Company.get_package_count('halfmile'),
        'quarter_mile': Company.get_package_count('quartermile'),
        'black_friday': Company.get_package_count('black_friday')
    }
    total_miles = (package_stats['one_mile'] + 
                  package_stats['half_mile'] * 0.5 + 
                  package_stats['quarter_mile'] * 0.25 +
                  package_stats['black_friday'])

    return render_template('dashboard/index.html', 
                         registrations=registrations,
                         package_stats=package_stats,
                         total_miles=total_miles,
                         now=datetime.utcnow())

# Only initialize database when running directly
if __name__ == '__main__':
    initialize_database()