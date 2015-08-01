from app.extensions import db
from datetime import datetime


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer(), primary_key=True)
    parentId = db.Column(db.Integer(), db.ForeignKey('comments.id'), nullable=True)

    userId = db.Column(db.Integer(), db.ForeignKey('users.id'))
    articleId = db.Column(db.Integer(), db.ForeignKey('articles.id'))

    subject = db.Column(db.String(200))
    message = db.Column(db.String(10000))
    lastModified = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    dateCreated = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)