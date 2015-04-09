from tests import BaseTestCase, BASEDIR
import json
import os


class APITestCase(BaseTestCase):

    def test_articles_to_json(self):
        response = self.client.get('/api/articles/')

        self.run_api(response, 'verified-articles.json')

    def test_categories_to_json(self):
        response = self.client.get('/api/categories/')

        self.run_api(response, 'verified-categories.json')

    def test_article_to_json(self):
        # request for the first article
        response = self.client.get('/api/articles/1/')

        self.run_api(response, 'verified-article.json')

    def get_verified_json(self, filename):
        """ Returns a dictionary from the given filename.
            NOTE: json file must be located in API fixture namespace `/tests/fixtures/api/`
        """
        path = os.path.join(BASEDIR, 'fixtures', 'api', filename)
        with open(path, 'r') as myfile:
            return json.loads(myfile.read())

    def run_api(self, resp, filename):
        self.assertEqual(resp.status_code, 200, 'status code failed')

        # convert response to a dictionary
        result = json.loads(resp.get_data())

        # retrieve the verified articles
        expected = self.get_verified_json(filename)

        # compare the response against the verified articles
        self.maxDiff = None
        self.assertDictEqual(expected, result, "json doesn't match")

