from tests import BaseTestCase


class AdminTestCase(BaseTestCase):

    def test_dashboard(self):
        r = self.client.get('/admin/')
        self.assertEqual(r.status_code, 200, 'status code failed')