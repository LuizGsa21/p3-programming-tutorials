import os
import pprint

from flask import session, current_app

# from app.extensions import Form, current_user
from app.extensions import current_user, Form
from app.helpers.utils import allowed_file
from app.models import User, Category
from wtforms import ValidationError, StringField, FileField, HiddenField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Length, Email
from werkzeug.datastructures import FileStorage
import imghdr
import json

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
    crop_data = HiddenField('crop_data', validators=[InputRequired()])

    def validate_avatar(self, field):
        fileStorage = field.data

        # if no file was provided we will use the original image
        if not isinstance(fileStorage, FileStorage):
            return

        # check the data signature for a valid image
        extension = imghdr.what(fileStorage)
        if extension not in current_app.config.get('ALLOWED_EXTENSIONS', ('',)):
            raise ValidationError('Only images are allowed...')

        # check file size
        fileStorage.seek(0, os.SEEK_END)
        size = fileStorage.tell()
        if size == 0:
            raise ValidationError("You can't upload an empty file.")
        fileStorage.seek(0, os.SEEK_SET)  # reset file pointer

        maxByteSize = current_app.config['MAX_UPLOAD_SIZE']
        if size > maxByteSize:
            raise ValidationError(
                'File size is too large... please choose an image smaller than ' + str(int(maxByteSize / 1024)) + ' KB')

    def validate_crop_data(self, field):

        data = json.loads(field.data)
        try:
            data = {
                'x': int(data['x']),
                'y': int(data['y']),
                'width': int(data['width']),
                'height': int(data['height'])
            }

        except Exception, e:
            print e
            raise ValueError('Invalid json data.')

        field.data = data