from tests import BaseTestCase


class UserTestCase(BaseTestCase):

    def test_profile(self):
        r = self.client.get('/user/profile/')
        self.assertEqual(r.status_code, 200, 'status code failed')

    def test_settings(self):
        r = self.client.get('/api/categories/')
        self.assertEqual(r.status_code, 200, 'status code failed')