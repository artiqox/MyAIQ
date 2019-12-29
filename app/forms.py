# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf          import FlaskForm
from flask_wtf.file     import FileField, FileRequired
from wtforms            import StringField, TextAreaField, SubmitField, PasswordField, RadioField
from wtforms.validators import InputRequired, Email, DataRequired

class LoginForm(FlaskForm):
	type        = RadioField   (u'Login with:', choices=[('TG','telegram'),('TW','twitter')], default="TG", validators=[DataRequired()])
	username    = StringField  (u'Username'        , validators=[DataRequired()])
	password    = PasswordField(u'Password'        , validators=[DataRequired()])

class RegisterForm(FlaskForm):
	type        = RadioField   ('Register with:', choices=[('TG','telegram'),('TW','twitter')], default="TG", validators=[DataRequired()])
	name        = StringField  (u'Name'      )
	username    = StringField  (u'Username'  , validators=[DataRequired()])
	password    = PasswordField(u'Password'  , validators=[DataRequired()])
	#email       = StringField  (u'Email'     , validators=[DataRequired(), Email()])
