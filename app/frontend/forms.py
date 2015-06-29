from app.models import User, Category
from flask_wtf import Form
from wtforms import StringField, PasswordField, ValidationError, HiddenField, TextAreaField, IntegerField
from wtforms.validators import InputRequired, EqualTo, Length, Email, Regexp


def length_validator(name, min, max):
    return Length(min=min, max=max, message='%s field must be between %s and %s characters long.' % (name, min, max))


class RegisterForm(Form):
    username = StringField('Username', validators=[InputRequired(), length_validator('Username', 4, 12)])
    email = StringField('Email', validators=[InputRequired(), Email(message='Email field is invalid')])
    password = PasswordField(
        'Password', validators=[
            InputRequired(),
            length_validator('Password', 6, 50)
            # EqualTo('confirm', message='Passwords must match')
        ])
    # confirm = PasswordField('Confirm Password', [InputRequired()])

    def validate_username(self, field):
        existing_user = User.query.filter_by(username_insensitive=field.data).first()
        if existing_user:
            raise ValidationError('Username "' + field.data + '" is taken.')

    def validate_email(self, field):
        existing_user = User.query.filter_by(email=field.data).first()
        if existing_user:
            raise ValidationError(field.data + ' is already registered...')


class LoginForm(Form):
    # username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Regexp('[a-zA-z@.]', message='error')])
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