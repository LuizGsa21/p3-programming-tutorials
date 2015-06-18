from extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import Comparator, hybrid_property
from sqlalchemy.sql import func
from sqlalchemy.ext.mutable import Mutable

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


class MutableList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(255), unique=True)

    # for oauth providers that don't guarantee user's email (GitHub)
    oauth_id = db.Column(db.String(50))
    oauth_provider = db.Column(db.String(50))

    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    pwdhash = db.Column(db.String(255))

    avatar = db.Column(db.String(255), default='default-avatar.jpg')
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)

    articles = db.relationship('Article', backref='author', lazy='dynamic')

    comments = db.relationship('Comment', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.pwdhash = generate_password_hash(self.pwdhash)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def is_admin(self):
        # Everyone is admin!!! :)
        return True

    @hybrid_property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    @hybrid_property
    def username_insensitive(self):
        return self.username.lower()

    @username_insensitive.comparator
    def username_insensitive(cls):
        return CaseInsensitiveWord(cls.username)

    @hybrid_property
    def email_insensitive(self):
        return self.email.lower()

    @email_insensitive.comparator
    def email_insensitive(cls):
        return CaseInsensitiveWord(cls.email)


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    articles = db.relationship('Article', backref='category', lazy='dynamic')

    def __str__(self):
        return self.name


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.String(20000))
    author_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer(), db.ForeignKey('categories.id'), nullable=False)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow)

    comments = db.relationship('Comment', backref='articles', lazy='dynamic')


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer(), primary_key=True)
    parent_id = db.Column(db.Integer(), db.ForeignKey('comments.id'), nullable=True)

    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer(), db.ForeignKey('articles.id'))

    subject = db.Column(db.String(200))
    message = db.Column(db.String(10000))
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