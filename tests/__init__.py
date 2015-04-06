import unittest
from app import create_app
from app.config import TestingConfig
from app.models import Article, Comment, User, db, Category


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing', config=TestingConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        reset_database()

    def tearDown(self):
        self.ctx.pop()


def reset_database():
    Comment.query.delete()
    Article.query.delete()
    User.query.delete()
    Category.query.delete()
    db.session.commit()

    db.session.add(Category(name='Python'))
    db.session.add(Category(name='Other'))
    db.session.commit()

    # create 2 users
    for i in range(2):
        db.session.add(User(
            username='user%s' % i,
            pwdhash='password'
        ))
    db.session.commit()

    # user1 has 4 articles
    user1 = User.query.get(1)
    for i in range(4):
        db.session.add(Article(
            body='some body',
            author_id=user1.id,
            title='some title %s' % i,
            category_id=1
        ))

    # user2 has 2 articles
    user2 = User.query.get(2)

    for i in range(2):
        db.session.add(Article(
            body='some body',
            author_id=user2.id,
            title='some title %s' % i,
            category_id=2

        ))
    db.session.commit()

    # create comments
    user1_article = Article.query.filter_by(id=user1.id).first()
    comment1 = Comment(
        body='nice articles',
        article_id=user1_article.id,
    )
    db.session.add(comment1)
    db.session.commit()
    # reply to comment 1
    db.session.add(Comment(
        body='Thanks',
        article_id=user1_article.id,
        parent_comment_id=comment1.id
    ))
    db.session.commit()