from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    
    # Contact Person
    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    contact_photo = db.Column(db.String(200))
    
    # Sponsorship Details
    package_tier = db.Column(db.String(50), nullable=False)
    is_black_friday = db.Column(db.Boolean, default=False)
    payment_date = db.Column(db.DateTime)
    tickets_allocated = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def get_package_count(package_tier):
        """Get the count of registrations for a specific package tier"""
        return Company.query.filter_by(package_tier=package_tier).count()
    
    @staticmethod
    def check_registration_availability(package_tier):
        """Check if registration is available for the selected package"""
        if package_tier == 'black_friday':
            current_count = Company.get_package_count('black_friday')
            return current_count < 10, 10 - current_count
        return True, None  # No limit for other packages
