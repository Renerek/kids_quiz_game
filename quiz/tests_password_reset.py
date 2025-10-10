from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from quiz.views_password_reset import PASSWORD_RESET_TOKENS, TOKEN_EXPIRY_MINUTES
from django.core import mail
from django.conf import settings
from django.utils import timezone

class PasswordResetFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="resetuser", password="pw12345", email="reset@example.com")

    def test_password_reset_request_and_confirm(self):
        # Request password reset
        resp = self.client.post(reverse("quiz:password_reset_request"), {"email": "reset@example.com"}, follow=True)
        self.assertContains(resp, "Password reset email sent", status_code=200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Reset your Kids Quiz Game password")
        self.assertIn("reset@example.com", mail.outbox[0].to)
        # Find the token
        token = None
        for t, data in PASSWORD_RESET_TOKENS.items():
            if data["user_id"] == self.user.id:
                token = t
                break
        self.assertIsNotNone(token)
        # Visit confirm page
        resp = self.client.get(reverse("quiz:password_reset_confirm", args=[token]))
        self.assertContains(resp, "Set a New Password", status_code=200)
        # Submit new password
        resp = self.client.post(reverse("quiz:password_reset_confirm", args=[token]), {
            "new_password1": "newpass123",
            "new_password2": "newpass123"
        }, follow=True)
        self.assertContains(resp, "Password reset successful", status_code=200)
        self.assertEqual(len(mail.outbox), 2)
        confirmation_email = mail.outbox[-1]
        self.assertEqual(confirmation_email.subject, "Your Kids Quiz Game password has been reset")
        self.assertEqual(confirmation_email.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertIn("reset@example.com", confirmation_email.to)
        # Token should be deleted
        self.assertNotIn(token, PASSWORD_RESET_TOKENS)
        # User can now log in with new password
        login = self.client.login(username="resetuser", password="newpass123")
        self.assertTrue(login)

    def test_invalid_token(self):
        resp = self.client.get(reverse("quiz:password_reset_confirm", args=["invalidtoken"]))
        self.assertContains(resp, "Invalid or expired", status_code=200)

    def test_expired_token(self):
        # Create a token manually
        token = "expiredtoken123"
        PASSWORD_RESET_TOKENS[token] = {"user_id": self.user.id, "created": timezone.now() - timezone.timedelta(minutes=TOKEN_EXPIRY_MINUTES + 1)}
        resp = self.client.get(reverse("quiz:password_reset_confirm", args=[token]))
        self.assertContains(resp, "expired", status_code=200)
        self.assertNotIn(token, PASSWORD_RESET_TOKENS)
