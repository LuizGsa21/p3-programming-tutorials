from app.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .sqlalchemy_helpers import DefaultUserMixin


class User(db.Model, DefaultUserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), unique=True)  # TODO: lower limit to 15
    email = db.Column(db.String(255), unique=True)

    # for oauth providers that don't guarantee user's email (GitHub)
    oauthId = db.Column(db.String(50))
    oauthProvider = db.Column(db.String(50))

    firstName = db.Column(db.String(50))
    lastName = db.Column(db.String(50))

    pwdhash = db.Column(db.String(255))

    avatar = db.Column(db.String(255), default='avatar.jpg')
    dateJoined = db.Column(db.DateTime(), default=datetime.utcnow)

    articles = db.relationship('Article', backref='author', lazy='dynamic')

    comments = db.relationship('Comment', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.pwdhash = generate_password_hash(self.pwdhash)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)