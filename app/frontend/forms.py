from app.extensions import current_user
from app.models import User, Category
from flask_wtf import Form
from wtforms import StringField, PasswordField, ValidationError, HiddenField, TextAreaField, IntegerField
from wtforms.validators import InputRequired, EqualTo, Length, Email


class RegisterForm(Form):
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
        if existing_user and current_user.id != existing_user.id:
            raise ValidationError('This email is taken.')

class LoginForm(Form):
    # username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])

class CommentForm(Form):
    article_id = HiddenField('id', validators=[InputRequired()])
    subject = StringField('Subject', validators=[InputRequired()])
    message = TextAreaField('Message', validators=[InputRequired()])
    parent_id = HiddenField('id')

    def validate_parent_id(self, field):
        data = field.data
        try:
            data = int(data)
        except ValueError:
            data = None
        field.data = data