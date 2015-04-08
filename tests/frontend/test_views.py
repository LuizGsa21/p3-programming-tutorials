from tests import BaseTestCase
from app.models import User, db


class FrontendTestCase(BaseTestCase):
    def test_index(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200, 'status code failed')

    def test_login_logout(self):
        r = self.client.post('/login/', data={
            'username': 'Bob',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        self.assertTrue('You have successfully logged in.' in r.get_data())

        r = self.client.get('/logout/', follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        self.assertTrue('You have successfully logged out.' in r.get_data())

    def test_register(self):
        total = User.query.count()

        r = self.client.post('/register/', data={
            'username': 'Batman',
            'password': 'password',
            'confirm': 'password'
        }, follow_redirects=True)

        self.assertEqual(r.status_code, 200)

        # rollback in case commit wasn't called
        db.session.rollback()
        new_total = User.query.count()
        self.assertEqual(total + 1, new_total, 'Failed to register user `Batman`')