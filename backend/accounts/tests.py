from django.core import mail
from django.test import override_settings
from rest_framework.test import APITestCase

from .models import User
from .verification import make_token


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class RegistrationTests(APITestCase):
    def test_only_kbtu_emails_can_sign_up(self):
        response = self.client.post("/api/auth/register/", {"email": "someone@gmail.com", "password": "Str0ng-pass-123"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.exists())

    def test_sign_up_sends_verification_link_and_account_is_inactive(self):
        response = self.client.post("/api/auth/register/", {"email": "a_student@kbtu.kz", "password": "Str0ng-pass-123"})
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email="a_student@kbtu.kz")
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/verify?token=", mail.outbox[0].body)

    def test_login_is_blocked_until_email_is_verified(self):
        User.objects.create_user(email="a_student@kbtu.kz", password="Str0ng-pass-123", is_active=False)
        response = self.client.post("/api/auth/login/", {"email": "a_student@kbtu.kz", "password": "Str0ng-pass-123"})
        self.assertEqual(response.status_code, 403)

    def test_verification_activates_account_and_login_returns_token(self):
        user = User.objects.create_user(email="a_student@kbtu.kz", password="Str0ng-pass-123", is_active=False)
        response = self.client.get("/api/auth/verify/", {"token": make_token(user)})
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/api/auth/login/", {"email": "a_student@kbtu.kz", "password": "Str0ng-pass-123"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)

    def test_broken_verification_token_is_rejected(self):
        response = self.client.get("/api/auth/verify/", {"token": "not-a-real-token"})
        self.assertEqual(response.status_code, 400)
