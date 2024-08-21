# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class ConnectWithCleanerForm(FlaskForm):
    location = StringField('Country', validators=[DataRequired()])
    service = SelectField('Select Service', choices=[
        ('general_cleaning', 'General House Cleaning'),
        ('laundry', 'Laundry Service'),
        ('cleaning_laundry', 'House Cleaning with Laundry')
    ], validators=[DataRequired()])
    submit = SubmitField('Submit')
