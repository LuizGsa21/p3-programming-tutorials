from tests import BaseTestCase


class UserTestCase(BaseTestCase):

    def test_status_code(self):
        r = self.client.get('/user/profile/')
        self.assertEqual(r.status_code, 200, 'status code failed')

        r = self.client.get('/user/settings/')
        self.assertEqual(r.status_code, 200, 'status code failed')