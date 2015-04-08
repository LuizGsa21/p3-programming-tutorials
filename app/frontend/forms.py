from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, EqualTo


class RegistrationForm(Form):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField(
        'Password', validators=[
            InputRequired(), EqualTo('confirm', message='Passwords must match')
        ])
    confirm = PasswordField('Confirm Password', [InputRequired()])


class LoginForm(Form):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])