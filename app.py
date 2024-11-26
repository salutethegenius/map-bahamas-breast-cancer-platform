import os
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.debug = True  # Enable debug mode to test the feature

# Configuration
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

from models import Company, User
from forms import CompanyRegistrationForm, LoginForm

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Successfully logged in!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password. Please try admin@mapbahamas.com', 'error')
    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
db.init_app(app)
mail = Mail(app)

from models import Company
from forms import CompanyRegistrationForm

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Create uploads directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    form = CompanyRegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Handle file upload
            photo_filename = None
            if form.contact_photo.data:
                file = form.contact_photo.data
                if file.filename:
                    photo_filename = secure_filename(file.filename)
                    try:
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
                    except Exception as e:
                        flash(f'Error uploading file: {str(e)}', 'error')
                        return render_template('register.html', form=form)

            # Create company record
            company = Company(
                name=form.company_name.data,
                address=form.company_address.data,
                email=form.company_email.data,
                phone=form.company_phone.data,
                contact_name=form.contact_name.data,
                contact_email=form.contact_email.data,
                contact_phone=form.contact_phone.data,
                contact_photo=photo_filename,
                package_tier=form.package_tier.data,
                is_black_friday=form.package_tier.data == 'black_friday',
                tickets_allocated=5 if form.package_tier.data == 'black_friday' else 0
            )
            
            db.session.add(company)
            db.session.commit()
            
            # Send welcome email
            send_welcome_email(company)
            
            flash('Registration successful!', 'success')
            return redirect(url_for('confirmation'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
            return render_template('register.html', form=form)
    
    return render_template('register.html', form=form)

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

def send_welcome_email(company):
    msg = Message(
        'Welcome to MAP Bahamas Sponsorship Program',
        sender='noreply@mapbahamas.com',
        recipients=[company.email]
    )
    msg.html = render_template(
        'email/welcome.html',
        company=company
    )
    mail.send(msg)

@app.route('/load-test-data', methods=['POST'])
def load_test_data():
    if not app.debug:
        flash('Test data can only be loaded in debug mode.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Calculate payment dates for next month
        from datetime import datetime, timedelta
        today = datetime.now()
        next_month = today.replace(day=1) + timedelta(days=32)
        payment_date_1 = next_month.replace(day=15)
        payment_date_2 = next_month.replace(day=20)
        
        with db.session.begin():
            # 1 Mile Package sponsor
            company1 = Company(
                name='Tech Solutions Inc.',
                address='123 Innovation Drive, Nassau',
                email='contact@techsolutions.test',
                phone='1-242-555-0101',
                contact_name='John Smith',
                contact_email='john@techsolutions.test',
                contact_phone='1-242-555-0102',
                contact_photo='sponsor.jpeg',
                package_tier='1mile',
                payment_date=payment_date_1,
                is_black_friday=False,
                tickets_allocated=0
            )
            
            # Black Friday Special sponsor
            company2 = Company(
                name='Island Marketing Group',
                address='456 Bay Street, Nassau',
                email='info@islandmarketing.test',
                phone='1-242-555-0201',
                contact_name='Sarah Johnson',
                contact_email='sarah@islandmarketing.test',
                contact_phone='1-242-555-0202',
                contact_photo='blackfriday.jpeg',
                package_tier='black_friday',
                payment_date=payment_date_2,
                is_black_friday=True,
                tickets_allocated=5
            )
            
            db.session.add(company1)
            db.session.add(company2)
        
        flash('Test data has been successfully loaded!', 'success')
    except Exception as e:
        flash(f'Error loading test data: {str(e)}', 'error')
    
    return redirect(url_for('index'))

with app.app_context():
    db.create_all()
    # Recreate admin user
    admin_user = User.query.filter_by(email='admin@mapbahamas.com').first()
    if not admin_user:
        admin = User(email='admin@mapbahamas.com', is_admin=True)
        admin.set_password('adminpass123')
        db.session.add(admin)
        db.session.commit()
    else:
        # Update existing admin password
        admin_user.set_password('adminpass123')
        db.session.commit()
