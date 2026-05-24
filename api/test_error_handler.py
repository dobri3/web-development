from django.test import TestCase
from rest_framework.test import APIClient


class ErrorHandlerTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_404_format(self):

        response = self.client.get(
            "/api/movies/999999/"
        )

        self.assertEqual(
            response.status_code,
            404
        )

        self.assertFalse(
            response.data["success"]
        )

        self.assertIn(
            "error",
            response.data
        )