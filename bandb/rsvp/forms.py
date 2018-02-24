'''
Created on May 3, 2017

@author: wjgallag
'''

try:
    from flask_wtf import FlaskForm
except ImportError:
    from flask_wtf import Form as FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, RadioField, FieldList
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Length, Email
from wtforms.widgets import TableWidget, CheckboxInput

class VerifyForm(FlaskForm):
    last_name = StringField(validators=[InputRequired()])
    invite_code = StringField(validators=[InputRequired(), Length(min=4,max=4)])
    submit = SubmitField('Submit')

class ResponseForm(FlaskForm):
    attending = RadioField(choices=[(1, 'Love to!'), (0, 'Sadly cannot')], coerce=int, validators=[InputRequired()], widget=TableWidget(), default=1)
    submit = SubmitField('Submit')

class DetailsForm(FlaskForm):
    attendees = SelectMultipleField(coerce=int, validators=[InputRequired()], widget=TableWidget(), option_widget=CheckboxInput())
    guest = StringField(validators=[InputRequired()])
    email = EmailField(validators=[InputRequired(), Email()])
    lodging = StringField(validators=[InputRequired()])
    diet = StringField()
    songs = FieldList(StringField(), min_entries=1, max_entries=3)
    submit = SubmitField('Submit')

class SubmitForm(FlaskForm):
    submit = SubmitField('Submit')

