from tests import BaseTestCase, BASEDIR
import json
import os


class APITestCase(BaseTestCase):
    def test_articles_to_json(self):
        r = self.client.get('/api/articles/')

        self.assertEqual(r.status_code, 200, 'status code failed')

        data = json.loads(r.get_data())

        fixture_path = os.path.join(BASEDIR, 'api', 'verified-articles.json')
        with open(fixture_path, 'r') as fixture_file:
            expected = json.loads(fixture_file.read())

        # compare the response against the verified json
        self.assertDictEqual(expected, data, "json doesn't match")

    def test_categories_to_json(self):

        from tests.database_fixture import _categories

        expected = dict(categories=_categories)

        r = self.client.get('/api/categories/')

        data = json.loads(r.get_data())
        self.assertDictEqual(expected, data)

        self.assertEqual(r.status_code, 200, 'status code failed')