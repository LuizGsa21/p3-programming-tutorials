import unittest
import os

from app import create_app
from app.config import TestingConfig
from app.models import db
from tests.fixtures.database_fixture import get_database_fixtures


BASEDIR = os.path.dirname(os.path.abspath(__file__))


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config=TestingConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.test_request_context()
        self.ctx.push()

        reset_database()

    def tearDown(self):
        db.drop_all()
        self.ctx.pop()


def reset_database():
    fixtures = get_database_fixtures()
    import app.models as models

    for className, rows in fixtures.iteritems():
        table = getattr(models, className)
        for row in rows:
            db.session.add(table(**row))
            db.session.commit()