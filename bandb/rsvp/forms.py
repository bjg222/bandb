'''
Created on May 3, 2017

@author: wjgallag
'''

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, RadioField, FieldList
from wtforms.validators import InputRequired, Length
from wtforms.widgets import TableWidget, CheckboxInput

class VerifyForm(FlaskForm):
    last_name = StringField(validators=[InputRequired()])
    invite_code = StringField(validators=[InputRequired(), Length(min=4,max=4)])
    submit = SubmitField('Submit')

class ResponseForm(FlaskForm):
    attending = RadioField(choices=[(1, 'Yes'), (0, 'No')], coerce=int, validators=[InputRequired()], widget=TableWidget(), default=1)
    submit = SubmitField('Submit')

class DetailsForm(FlaskForm):
    attendees = SelectMultipleField(coerce=int, validators=[InputRequired()], widget=TableWidget(), option_widget=CheckboxInput())
    guest = StringField(validators=[InputRequired()])
    diet = StringField()
    songs = FieldList(StringField(), min_entries=1, max_entries=3)
    submit = SubmitField('Submit')

class SubmitForm(FlaskForm):
    submit = SubmitField('Submit')

