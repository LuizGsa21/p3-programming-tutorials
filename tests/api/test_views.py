from tests import BaseTestCase, BASEDIR
import json
import os


class APITestCase(BaseTestCase):
    def test_articles_to_json(self):
        r = self.client.get('/api/articles/')

        self.assertEqual(r.status_code, 200, 'status code failed')

        data = json.loads(r.get_data())

        path = os.path.join(BASEDIR, 'api', 'verified-articles.json')
        with open(path, 'r') as myfile:
            expected = json.loads(myfile.read())

        # compare the response against the verified json
        self.assertDictEqual(expected, data, "json doesn't match")

    def test_categories_to_json(self):

        from tests.database_fixture import _categories

        expected = dict(categories=_categories)

        r = self.client.get('/api/categories/')

        data = json.loads(r.get_data())

        self.maxDiff = None
        self.assertDictEqual(expected, data)

        self.assertEqual(r.status_code, 200)

    def test_article_to_json(self):

        # request for the first article
        r = self.client.get('/api/articles/1/')
        self.assertEqual(r.status_code, 200)

        path = os.path.join(BASEDIR, 'api', 'verified-articles.json')
        # get the first article from the verified articles
        with open(path, 'r') as myfile:
            article = json.loads(myfile.read())['articles'][0]
            expected = dict(article=article)

        data = json.loads(r.get_data())
        self.maxDiff = None
        self.assertDictEqual(expected, data)
