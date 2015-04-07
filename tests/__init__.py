import unittest
from app import create_app
from app.config import TestingConfig
from app.models import Article, Comment, User, db, Category
from database_fixture import get_database_fixtures
import os

BASEDIR = os.path.dirname(os.path.abspath(__file__))


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

    fixtures = get_database_fixtures()
    import app.models as models

    for className, rows in fixtures.iteritems():
        table = getattr(models, className)
        for row in rows:
            db.session.add(table(**row))
            db.session.commit()