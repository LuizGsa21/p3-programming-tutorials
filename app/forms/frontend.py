from app.models import User
from flask_wtf import Form
from wtforms import StringField, PasswordField, ValidationError, HiddenField, TextAreaField, IntegerField
from wtforms.validators import InputRequired, Length, Email, Regexp
from .wtf_custom_fields import strip_filter, length_validator, HiddenInteger


validators = {
    'username': [
        InputRequired(),
        Regexp('^[A-Za-z0-9]*$', message='Username may only contain letters and numbers'),
        length_validator('Username', 4, 12)
    ],
    'email': [
        InputRequired(),
        Email(message='Email field is invalid')
    ],
    'password': [
        InputRequired(),
        length_validator('Password', 6, 50)
    ]
}


class RegisterForm(Form):
    username = StringField('Username', validators=validators['username'], filters=[strip_filter])
    email = StringField('Email', validators=validators['email'], filters=[strip_filter])
    password = PasswordField('Password', validators=validators['password'])

    def validate_username(self, field):
        existing_user = User.query.filter_by(username_insensitive=field.data).first()
        if existing_user:
            raise ValidationError('Username "' + field.data + '" is taken.')

    def validate_email(self, field):
        existing_user = User.query.filter_by(email=field.data).first()
        if existing_user:
            raise ValidationError(field.data + ' is already registered...')


class LoginForm(Form):
    email = StringField('Email or Username', validators=[InputRequired()], filters=[strip_filter])
    password = PasswordField('Password', validators=[InputRequired()])


class BaseReplyForm(Form):
    message = TextAreaField('Message',
                            validators=[InputRequired(), Length(min=1, message='Message field is required')],
                            filters=[strip_filter])


class AddReplyForm(BaseReplyForm):
    articleId = HiddenInteger(validators=[InputRequired()])
    parentId = HiddenInteger(validators=[InputRequired()])


class EditReplyForm(BaseReplyForm):
    id = HiddenField(validators=[InputRequired()])


class BaseCommentForm(Form):
    subject = StringField('Subject', validators=[InputRequired()])
    message = TextAreaField('Message', validators=[InputRequired()])


class AddCommentForm(BaseCommentForm):
    articleId = HiddenInteger(validators=[InputRequired()])


class EditCommentForm(BaseCommentForm):
    id = HiddenField(validators=[InputRequired()])