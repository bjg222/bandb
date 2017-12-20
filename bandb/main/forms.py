'''
Created on May 3, 2017

@author: wjgallag
'''
try:
    from flask_wtf import FlaskForm
except ImportError:
    from flask_wtf import Form as FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Email

class EmailForm(FlaskForm):
    name = StringField(validators=[InputRequired()])
    email = EmailField(validators=[InputRequired(), Email()])
    submit = SubmitField('Submit')
