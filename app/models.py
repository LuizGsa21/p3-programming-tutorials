from extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import Comparator, hybrid_property
from sqlalchemy.sql import func
from utils import format_datetime

class CaseInsensitiveWord(Comparator):
    """Hybrid value representing a lower case representation of a word."""

    def __init__(self, word):
        if isinstance(word, basestring):
            self.word = word.lower()
        elif isinstance(word, CaseInsensitiveWord):
            self.word = word.word
        else:
            self.word = func.lower(word)

    def operate(self, op, other):
        if not isinstance(other, CaseInsensitiveWord):
            other = CaseInsensitiveWord(other)
        return op(self.word, other.word)

    def __clause_element__(self):
        return self.word

    def __str__(self):
        return self.word

# monkey patch to db.Model. used as a convenience method for populating values from a wtform
def populate_form(model, form):
    fields = form.data
    for column, value in fields.items():
        if hasattr(model, column):
            setattr(model, column, value)

setattr(db.Model, 'populate_form', populate_form)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(255), unique=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    pwdhash = db.Column(db.String(255))
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)

    articles = db.relationship('Article', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.pwdhash = generate_password_hash(self.pwdhash)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def is_admin(self):
        # Everyone is admin!!! :)
        return True


    @hybrid_property
    def username_insensitive(self):
        return CaseInsensitiveWord(self.username)

    @hybrid_property
    def email_insensitive(self):
        return CaseInsensitiveWord(self.email)

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(10), unique=True)
    articles = db.relationship('Article', backref='category', lazy='dynamic')

    def __str__(self):
        return self.name


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(20))
    body = db.Column(db.String(20000))
    author_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer(), db.ForeignKey('categories.id'), nullable=False)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow)

    comments = db.relationship('Comment', backref='articles', lazy='dynamic')


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer(), primary_key=True)
    body = db.Column(db.String(1000))
    article_id = db.Column(db.Integer(), db.ForeignKey('articles.id'))
    parent_comment_id = db.Column(db.Integer(), db.ForeignKey('comments.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    date_created = db.Column(db.DateTime(), default=datetime.utcnow)

# init database fixtures
def init_database():
    if Category.query.count() != 0:
        return
    categories = [
        {'id': 1, 'name': 'Python'},
        {'id': 2, 'name': 'PHP'},
        {'id': 3, 'name': 'Java'},
        {'id': 4, 'name': 'HTML'},
        {'id': 5, 'name': 'CSS'},
        {'id': 6, 'name': 'JavaScript'}
    ]
    for c in categories:
        db.session.add(Category(**c))
        db.session.commit()