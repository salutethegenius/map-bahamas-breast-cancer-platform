from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email, Length

class CompanyRegistrationForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=200)])
    company_address = TextAreaField('Company Address', validators=[DataRequired()])
    company_email = StringField('Company Email', validators=[DataRequired(), Email()])
    company_phone = StringField('Company Phone', validators=[DataRequired(), Length(min=7, max=20)])
    
    contact_name = StringField('Contact Person Name', validators=[DataRequired(), Length(min=2, max=100)])
    contact_email = StringField('Contact Email', validators=[DataRequired(), Email()])
    contact_phone = StringField('Contact Phone', validators=[DataRequired(), Length(min=7, max=20)])
    contact_photo = FileField('Contact Photo')
    
    package_tier = SelectField('Sponsorship Package', choices=[
        ('1mile', '1 Mile Package'),
        ('halfmile', '½ Mile Package'),
        ('quartermile', '¼ Mile Package'),
        ('black_friday', 'Black Friday Special (50% off)')
    ], validators=[DataRequired()])
