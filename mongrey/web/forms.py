# -*- coding: utf-8 -*-

from wtforms import TextField, PasswordField, validators, SubmitField
from flask_wtf import Form

from flask_wtf.form import _is_hidden

from .extensions import gettext

def _is_required(field):
    for validator in field.validators:
        if isinstance(validator, (validators.DataRequired, validators.InputRequired)):
            return True
    return False

class LoginForm(Form):

    username = TextField('Username', validators=[validators.DataRequired()])
    
    password = PasswordField('Password', validators=[validators.DataRequired()])
    
    submit = SubmitField(gettext(u"Login"))
                         
