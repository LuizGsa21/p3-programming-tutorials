from extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    pwdhash = db.Column(db.String)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    articles = db.relationship('Article', backref='author', lazy='dynamic')


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    body = db.Column(db.String)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship('Category')
    comments = db.relationship('Comment', backref='article', lazy='dynamic')


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
