from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
User = get_user_model()


class UserViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username = "user",
            email="user@mail.com",
            password="pass123"
        )

    # REGISTRATION ##############################################
    @patch("users.views.send_confirmation_email.delay")
    def test_user_registration_ok(self, mock_delay):
        response = self.client.post(
            reverse("users:user_create"),
            {
                "email": "test@test.com",
                "password": "12345678"
            }
        )

        self.assertEqual(response.status_code, 201)
        mock_delay.assert_called_once()

    # JWT #######################################################
    def test_jwt_token_obtain(self):
        response = self.client.post(
            reverse("users:token"),
            {
                "email": "user@mail.com",
                "password": "pass123"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_jwt_token_refresh(self):
        token = self.client.post(
            reverse("users:token"),
            {
                "email": "user@mail.com",
                "password": "pass123"
            }
        ).data["refresh"]

        response = self.client.post(
            reverse("users:refresh_token"),
            {"refresh": token}
        )
        self.assertEqual(response.status_code, 200)
