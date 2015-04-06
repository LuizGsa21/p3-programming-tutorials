from tests import BaseTestCase


class APITestCase(BaseTestCase):
    def test_status_code(self):
        r = self.client.get('/api/')
        self.assertEqual(r.status_code, 200, 'status code failed')