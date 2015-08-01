from app.extensions import db
from datetime import datetime
from flask import url_for

class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.String(20000))
    authorId = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    categoryId = db.Column(db.Integer(), db.ForeignKey('categories.id'), nullable=False)
    dateCreated = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    lastModified = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)

    comments = db.relationship('Comment', backref='articles', lazy='dynamic')

    @property
    def url(self):
        return url_for('frontend.article', category=self.category.name, articleId=self.id, title=self.title)