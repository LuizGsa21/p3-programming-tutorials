import os

from flask import session, current_app

# from app.extensions import Form, current_user
from app.extensions import current_user, Form
from app.helpers.utils import allowed_file
from app.models import User, Category
from wtforms import ValidationError, StringField, FileField, HiddenField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Length, Email
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
        if not current_user.is_admin() and not session.get('change-username'):
            raise ValidationError('You do not have permission to change your username.')

        existing_user = User.query.filter_by(username_insensitive=field.data).first()
        if existing_user and existing_user.id != current_user.id:
            raise ValidationError('Sorry this username is taken... please choose another.')


class UploadAvatarForm(Form):
    avatar = FileField('Upload Image')

    def validate_avatar(self, field):
        fileStorage = field.data

        if not isinstance(fileStorage, FileStorage):
            raise ValidationError("Please include a file before submission.")
        # check file size
        fileStorage.seek(0, os.SEEK_END)
        size = fileStorage.tell()
        if size == 0:
            raise ValidationError("You can't upload an empty file.")
        fileStorage.seek(0, os.SEEK_SET) # reset file pointer

        maxByteSize = current_app.config['MAX_UPLOAD_SIZE']
        print maxByteSize
        if size > maxByteSize:
            raise ValidationError(
                'File size is too large... please choose an image smaller than ' + str(int(maxByteSize/1024)) +' KB')
        if not allowed_file(fileStorage.filename):
            raise ValidationError('Only images are allowed...')