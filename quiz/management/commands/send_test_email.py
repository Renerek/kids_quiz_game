from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = "Send a single test email using current email backend. Useful for smoke-testing SMTP settings."

    def add_arguments(self, parser):
        parser.add_argument("recipient", nargs="?", help="Recipient email address", default=None)

    def handle(self, *args, **options):
        recipient = options.get("recipient") or settings.DEFAULT_FROM_EMAIL
        subject = "Kids Quiz Game - Test email"
        message = "This is a test email to verify SMTP settings. If you received this, SMTP is working."
        from_email = settings.DEFAULT_FROM_EMAIL

        self.stdout.write(f"Sending test email to: {recipient}")
        try:
            send_mail(subject, message, from_email, [recipient], fail_silently=False)
            self.stdout.write(self.style.SUCCESS("Test email sent (or written by file backend)."))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Failed to send test email: {exc}"))
            raise
