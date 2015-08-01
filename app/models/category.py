from app.extensions import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    articles = db.relationship('Article', backref='category', lazy='dynamic')

    def __str__(self):
        return self.name