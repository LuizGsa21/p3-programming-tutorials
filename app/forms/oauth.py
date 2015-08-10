from flask_wtf import Form
from wtforms import StringField, ValidationError
from .wtf_custom_fields import strip_filter
from .frontend import validators
from app.models import User


class RegisterUsernameForm(Form):
    username = StringField('Username', validators=validators['username'], filters=[strip_filter])

    def validate_username(self, field):
        existing_user = User.query.filter_by(username_insensitive=field.data).first()
        if existing_user:
            raise ValidationError('Username "' + field.data + '" is taken.')

    def validate_email(self, field):
        existing_user = User.query.filter_by(email=field.data).first()
        if existing_user:
            raise ValidationError(field.data + ' is already registered...')