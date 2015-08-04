from app.extensions import db
from .sqlalchemy_helpers import CaseInsensitiveWord
from sqlalchemy.ext.hybrid import Comparator, hybrid_property


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    articles = db.relationship('Article', backref='category', lazy='dynamic')

    @hybrid_property
    def name_insensitive(self):
        return self.name.lower()

    @name_insensitive.comparator
    def name_insensitive(self):
        return CaseInsensitiveWord(self.name)

    def __str__(self):
        return self.name