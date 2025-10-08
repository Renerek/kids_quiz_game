import os
import re
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings


class PasswordResetEmailContentsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='contenttest', password='pw12345', email='contenttest@example.com')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend', EMAIL_FILE_PATH=os.path.join(os.path.dirname(__file__), '..', 'sent_emails'))
    def test_password_reset_email_contains_subject_and_reset_link(self):
        path = settings.EMAIL_FILE_PATH
        os.makedirs(path, exist_ok=True)
        # Clean directory
        for fname in os.listdir(path):
            full = os.path.join(path, fname)
            if os.path.isfile(full):
                os.remove(full)

        resp = self.client.post(reverse('quiz:password_reset_request'), {'email': 'contenttest@example.com'}, follow=True)
        self.assertEqual(resp.status_code, 200)

        # Get the newest file
        files = sorted([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
        self.assertTrue(files, 'No email files written')
        newest = os.path.join(path, files[-1])

        content = open(newest, 'r', encoding='utf-8').read()
        # Check subject
        self.assertIn('Subject: Reset', content)
        # Extract URL-like substring from the file (http...)
        m = re.search(r'https?://[^\s]+', content)
        self.assertIsNotNone(m, 'No URL found in email content')
        url = m.group(0)
        # The URL should point to password_reset_confirm (contains '/quiz/password-reset/confirm/')
        self.assertIn('/quiz/password-reset/', url)
        self.assertIn('confirm', url)
