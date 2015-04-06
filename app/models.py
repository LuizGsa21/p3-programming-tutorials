from extensions import db
from sqlalchemy.sql.expression import func


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    pwdhash = db.Column(db.String)
    date_joined = db.Column(db.DateTime, default=func.current_timestamp())


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    body = db.Column(db.String)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_create = db.Column(db.DateTime, default=func.current_timestamp())


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    date_create = db.Column(db.DateTime, default=func.current_timestamp())
