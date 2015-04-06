from tests import BaseTestCase


class AdminTestCase(BaseTestCase):

    def test_status_code(self):
        r = self.client.get('/admin/')
        self.assertEqual(r.status_code, 200, 'status code failed')