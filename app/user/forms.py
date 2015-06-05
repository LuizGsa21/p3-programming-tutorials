from flask_wtf import Form
from wtforms import StringField, PasswordField, ValidationError, TextAreaField
# import wtforms.ext.sqlalchemy.fields
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, EqualTo, Length, Email
from app.models import User, Category

class AddArticleForm(Form):
    title = StringField('Title', validators=[InputRequired(), Length(min=4, max=20)])
    category = QuerySelectField('Category', query_factory=lambda: Category.query.all(), validators=[InputRequired()])
    body = TextAreaField('Body', validators=[InputRequired()])