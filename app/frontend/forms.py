from flask_wtf import Form
from wtforms import StringField, PasswordField, ValidationError
from wtforms.validators import InputRequired, EqualTo, Length, Email
from app.models import User, Category


class RegistrationForm(Form):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=12)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField(
        'Password', validators=[
            InputRequired(), Length(min=6, max=50)# EqualTo('confirm', message='Passwords must match')
        ])
    # confirm = PasswordField('Confirm Password', [InputRequired()])
    def validate_username(self, field):
        existing_user = User.query.filter_by(username_insensitive=field.data).first()
        if existing_user:
            raise ValidationError('This username is taken.')

    def validate_email(self, field):
        existing_user = User.query.filter_by(email=field.data).first()
        if existing_user:
            raise ValidationError('This email is taken.')

class LoginForm(Form):
    # username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])

class OpenIDForm(Form):
    openid = StringField('OpenID', validators=[InputRequired()])