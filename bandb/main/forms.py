'''
Created on May 3, 2017

@author: wjgallag
'''

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Email

class EmailForm(FlaskForm):
    name = StringField(validators=[InputRequired()])
    email = EmailField(validators=[InputRequired(), Email()])
    submit = SubmitField('Submit')
