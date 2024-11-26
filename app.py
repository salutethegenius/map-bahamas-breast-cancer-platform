import os
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

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

db.init_app(app)
mail = Mail(app)

from models import Company
from forms import CompanyRegistrationForm

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = CompanyRegistrationForm()
    
    if form.validate_on_submit():
        # Handle file upload
        photo_filename = None
        if form.contact_photo.data:
            file = form.contact_photo.data
            photo_filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        
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

with app.app_context():
    db.create_all()
