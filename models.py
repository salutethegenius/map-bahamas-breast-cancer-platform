from app import db
from datetime import datetime

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
