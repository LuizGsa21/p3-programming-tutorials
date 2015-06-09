from flask_wtf import Form
from app.extensions import current_user
from wtforms import StringField, PasswordField, ValidationError, TextAreaField, HiddenField
# import wtforms.ext.sqlalchemy.fields
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, EqualTo, Length, Email
from app.models import User, Category, Article

# Article forms
class AddArticleForm(Form):
    title = StringField('Title', validators=[InputRequired(), Length(min=4, max=20)])
    category = QuerySelectField('Category', query_factory=lambda: Category.query.all(), validators=[InputRequired()])
    body = TextAreaField('Body', validators=[InputRequired()])

class EditArticleForm(AddArticleForm):
    id = HiddenField('id', validators=[InputRequired()])

class DeleteArticleForm(Form):
    id = HiddenField('id', validators=[InputRequired()])

# User Forms
class EditProfileForm(Form):
    email = StringField('Email', validators=[InputRequired()])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])