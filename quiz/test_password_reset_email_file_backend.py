from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
import os


class PasswordResetFileBackendTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='filetest', password='pw12345', email='filetest@example.com')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend', EMAIL_FILE_PATH=os.path.join(os.path.dirname(__file__), '..', 'sent_emails'))
    def test_password_reset_writes_email_file(self):
        # Ensure directory exists and is empty
        path = settings.EMAIL_FILE_PATH
        os.makedirs(path, exist_ok=True)
        # Clean directory
        for fname in os.listdir(path):
            full = os.path.join(path, fname)
            if os.path.isfile(full):
                os.remove(full)

        resp = self.client.post(reverse('quiz:password_reset_request'), {'email': 'filetest@example.com'}, follow=True)
        # Should redirect back to request page with a success message
        self.assertEqual(resp.status_code, 200)
        # There should be at least one file written
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        self.assertTrue(len(files) >= 1, f'No email files found in {path}')
