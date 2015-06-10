import pprint
from flask import session
import os
# from app.extensions import Form, current_user
from app.extensions import current_user, Form
from app.utils import allowed_file
from app.models import User, Category, Article
from wtforms import ValidationError, StringField, PasswordField, FileField, HiddenField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, EqualTo, Length, Email
from werkzeug.datastructures import FileStorage
# Article forms
class AddArticleForm(Form):
    title = StringField('Title', validators=[InputRequired(), Length(min=1, max=250)])
    category = QuerySelectField('Category', query_factory=lambda: Category.query.all(), validators=[InputRequired()])
    body = TextAreaField('Body', validators=[InputRequired()])


class EditArticleForm(AddArticleForm):
    id = HiddenField('id', validators=[InputRequired()])


class DeleteArticleForm(Form):
    id = HiddenField('id', validators=[InputRequired()])


class EditProfileForm(Form):
    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])

    def validate_username(self, field):
        if not current_user.is_admin() and not session.get('change-username-allowed'):
            raise ValidationError('You do not have permission to change your username.')

        existing_user = User.query.filter_by(username_insensitive=field.data).first()
        if existing_user and existing_user.id != current_user.id:
            raise ValidationError('Sorry this username is taken... please choose another.')


class UploadAvatarForm(Form):
    avatar = FileField('Profile Avatar')

    def validate_avatar(self, field):
        fileStorage = field.data

        if not isinstance(fileStorage, FileStorage):
            raise ValidationError("Please include a file before submission.")
        # check file size
        if fileStorage.tell() == 0:
            raise ValidationError("You can't upload an empty file.")
        fileStorage.seek(0, os.SEEK_SET) # reset file pointer

        if not allowed_file(fileStorage.filename):
            raise ValidationError('Only images are allowed...')