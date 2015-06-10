from flask import session
from app.extensions import Form, current_user
from app.models import User, Category, Article
from wtforms import StringField, PasswordField, ValidationError, TextAreaField, HiddenField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, EqualTo, Length, Email

# Article forms
class AddArticleForm(Form):
    title = StringField('Title', validators=[InputRequired(), Length(min=1, max=250)])
    category = QuerySelectField('Category', query_factory=lambda: Category.query.all(), validators=[InputRequired()])
    body = TextAreaField('Body', validators=[InputRequired()])

class EditArticleForm(AddArticleForm):
    id = HiddenField('id', validators=[InputRequired()])

class DeleteArticleForm(Form):
    id = HiddenField('id', validators=[InputRequired()])

# User Forms
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