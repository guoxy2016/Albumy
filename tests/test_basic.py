from flask import current_app

from .base import BaseTestCase


class BasicTestCase(BaseTestCase):
    def test_app_exist(self):
        self.assertFalse(current_app is None)

    def test_is_testing(self):
        self.assertTrue(current_app.testing)
        self.assertTrue(current_app.config['TESTING'])

    def test_404_error(self):
        response = self.client.get('/nothing')
        self.assertIn('The requested URL was not found on the server', response.get_data(as_text=True))
        self.assertEqual(response.status_code, 404)
