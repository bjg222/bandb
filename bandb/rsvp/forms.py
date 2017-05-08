'''
Created on May 3, 2017

@author: wjgallag
'''

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, RadioField
from wtforms.validators import InputRequired, Length, Optional
from wtforms.widgets import TableWidget, CheckboxInput

class VerifyForm(FlaskForm):
    last_name = StringField('Please enter your last name', validators=[InputRequired()])
    invite_code = StringField('Please enter the code from your invitation', validators=[InputRequired(), Length(min=4,max=4)])
    submit = SubmitField('Submit')

# def str_to_bool(s):
#     return s in ['yes', 'Yes', 'y', 'Y', 'true', 'True', 't', 'T']

class RsvpForm(FlaskForm):
    attending = RadioField('Please indicate if you will be attending', choices=[(1, 'Yes'), (0, 'No')], coerce=int, validators=[InputRequired()], widget=TableWidget(), default=1)
    submit = SubmitField('Submit')

# class MultiCheckboxField(SelectMultipleField):
#     widget = TableWidget()
#     option_widget = CheckboxInput()

class RsvpDetailsForm(FlaskForm):
    attendees = SelectMultipleField('Please indicate who will be attending', coerce=int, validators=[InputRequired()], widget=TableWidget(), option_widget=CheckboxInput())
    guest = StringField('Please enter the name of your guest')
    submit = SubmitField('Submit')