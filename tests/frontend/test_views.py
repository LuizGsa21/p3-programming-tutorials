from tests import BaseTestCase


class FrontendTestCase(BaseTestCase):
    def test_index(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200, 'status code failed')