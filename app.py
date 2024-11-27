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
    # Get Black Friday package availability
    _, black_friday_remaining = Company.check_registration_availability('black_friday')
    package_stats = {
        'black_friday': Company.get_package_count('black_friday'),
        'one_mile': Company.get_package_count('1mile'),
        'half_mile': Company.get_package_count('halfmile'),
        'quarter_mile': Company.get_package_count('quartermile')
    }
    return render_template('index.html', 
                         black_friday_remaining=black_friday_remaining,
                         package_stats=package_stats)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Create uploads directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    form = CompanyRegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Check if company email already exists
            existing_company = Company.query.filter_by(email=form.company_email.data).first()
            if existing_company:
                flash('A company with this email already exists.', 'error')
                return render_template('register.html', form=form)
            
            # Check package availability
            package_tier = form.package_tier.data
            is_available, remaining_spots = Company.check_registration_availability(package_tier)
            if not is_available:
                flash('Sorry, this package is no longer available.', 'error')
                return render_template('register.html', form=form)
            elif package_tier == 'black_friday' and remaining_spots is not None:
                flash(f'Black Friday Special: Only {remaining_spots} spots remaining!', 'info')

            # Handle file upload
            photo_filename = None
            if form.contact_photo.data:
                file = form.contact_photo.data
                if file.filename:
                    # Validate file type
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                    if '.' not in file.filename or \
                       file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                        flash('Invalid file type. Please upload an image file.', 'error')
                        return render_template('register.html', form=form)
                    
                    photo_filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
                    
                    try:
                        file.save(file_path)
                    except Exception as e:
                        flash(f'Error uploading file: {str(e)}', 'error')
                        return render_template('register.html', form=form)

            # Get payment date from form
            payment_date = request.form.get('payment_date')
            if not payment_date:
                flash('Please select a payment date.', 'error')
                return render_template('register.html', form=form)

            try:
                payment_date = datetime.strptime(payment_date, '%Y-%m-%d')
            except ValueError:
                flash('Invalid payment date format.', 'error')
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
                contact_photo=os.path.join('uploads', photo_filename) if photo_filename else None,
                package_tier=form.package_tier.data,
                is_black_friday=form.package_tier.data == 'black_friday',
                tickets_allocated=5 if form.package_tier.data == 'black_friday' else 0,
                payment_date=payment_date
            )
            
            db.session.add(company)
            db.session.commit()
            
            # Send welcome email
            try:
                send_welcome_email(company)
            except Exception as e:
                # Log the error but don't stop the registration process
                print(f"Error sending welcome email: {str(e)}")
            
            flash('Registration successful! Please check your email for further instructions.', 'success')
            return redirect(url_for('confirmation', id=company.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration. Please try again.', 'error')
            print(f"Registration error: {str(e)}")  # Log the actual error
            return render_template('register.html', form=form)
    
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return render_template('register.html', form=form)

@app.route('/confirmation')
def confirmation():
    company_id = request.args.get('id')
    if company_id:
        company = Company.query.get_or_404(company_id)
        return render_template('confirmation.html', company=company)
    flash('Registration not found', 'error')
    return redirect(url_for('index'))

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

@app.route('/dashboard')
@login_required
def dashboard():
    # Query all registrations
    registrations = Company.query.order_by(Company.created_at.desc()).all()
    
    # Get package statistics
    package_stats = {
        'black_friday': Company.get_package_count('black_friday'),
        'one_mile': Company.get_package_count('1mile'),
        'half_mile': Company.get_package_count('halfmile'),
        'quarter_mile': Company.get_package_count('quartermile')
    }
    
    # Calculate Black Friday availability
    black_friday_remaining = 10 - package_stats['black_friday']
    
    return render_template('dashboard/index.html', 
                         registrations=registrations,
                         package_stats=package_stats,
                         black_friday_remaining=black_friday_remaining,
                         now=datetime.utcnow())

@app.route('/registration/<int:id>')
@login_required
def registration_details(id):
    registration = Company.query.get_or_404(id)
    return render_template('dashboard/registration_details.html', 
                         registration=registration,
                         now=datetime.utcnow())


@app.route('/sponsor/<int:id>')
def sponsor_profile(id):
    sponsor = Company.query.get_or_404(id)
    return render_template('sponsor_profile.html', sponsor=sponsor)

@app.route('/export_registrations')
@login_required
def export_registrations():
    try:
        registrations = Company.query.order_by(Company.created_at.desc()).all()
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers with all fields
        writer.writerow([
            'Company Name', 'Company Address', 'Company Email', 'Company Phone',
            'Package Tier', 'Black Friday Special', 'Event Tickets',
            'Contact Name', 'Contact Email', 'Contact Phone',
            'Registration Date', 'Payment Date', 'Status'
        ])
        
        # Write data
        for reg in registrations:
            status = 'Paid' if reg.payment_date and reg.payment_date <= datetime.utcnow() else 'Pending'
            writer.writerow([
                reg.name, reg.address, reg.email, reg.phone,
                reg.package_tier, 'Yes' if reg.is_black_friday else 'No',
                '5' if reg.is_black_friday else '0',
                reg.contact_name, reg.contact_email, reg.contact_phone,
                reg.created_at.strftime('%Y-%m-%d'),
                reg.payment_date.strftime('%Y-%m-%d') if reg.payment_date else 'Not set',
                status
            ])
        
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=registrations.csv'}
        )
    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/reset_registrations')
@login_required
def reset_registrations():
    try:
        # Delete all companies but keep admin user
        Company.query.delete()
        db.session.commit()
        flash('All registrations have been reset successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error resetting registrations: {str(e)}', 'error')
    return redirect(url_for('dashboard'))