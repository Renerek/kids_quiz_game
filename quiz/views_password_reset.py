from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail, get_connection
import smtplib
import logging
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from .forms import CustomPasswordResetRequestForm, CustomSetPasswordForm
import datetime
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

# In-memory store for tokens (for demo; use a model in production)
PASSWORD_RESET_TOKENS = {}
TOKEN_EXPIRY_MINUTES = 30


def send_password_reset_confirmation_email(user, request):
    login_url = request.build_absolute_uri(reverse("quiz:login"))
    contact_url = request.build_absolute_uri(reverse("quiz:contact"))
    context = {
        "username": user.username,
        "login_url": login_url,
        "contact_url": contact_url,
        "reset_time": timezone.now(),
    }
    text_body = render_to_string("quiz/emails/password_reset_confirmation.txt", context)
    html_body = render_to_string("quiz/emails/password_reset_confirmation.html", context)
    msg = EmailMultiAlternatives(
        "Your Kids Quiz Game password has been reset",
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
    msg.attach_alternative(html_body, "text/html")
    try:
        msg.send(fail_silently=False)
    except smtplib.SMTPAuthenticationError:
        logging.exception("SMTP authentication failed when sending password reset confirmation email")
        try:
            file_conn = get_connection(
                "django.core.mail.backends.filebased.EmailBackend",
                file_path=settings.EMAIL_FILE_PATH,
            )
            file_conn.send_messages([msg])
        except Exception:
            logging.exception("Failed to write password reset confirmation email to file backend")
    except Exception:
        logging.exception("Failed to send password reset confirmation email")
        try:
            file_conn = get_connection(
                "django.core.mail.backends.filebased.EmailBackend",
                file_path=settings.EMAIL_FILE_PATH,
            )
            file_conn.send_messages([msg])
        except Exception:
            logging.exception("Failed to write password reset confirmation email to file backend after general failure")

def password_reset_request(request):
    if request.method == "POST":
        form = CustomPasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                # Do not embed HTML in messages; let the template show a signup link.
                messages.error(request, "No account found with that email.")
                return render(request, "quiz/password_reset_request.html", {"form": form, "show_signup_link": True})
            # Generate token
            token = get_random_string(32)
            PASSWORD_RESET_TOKENS[token] = {
                "user_id": user.id,
                "created": timezone.now(),
            }
            reset_url = request.build_absolute_uri(reverse("quiz:password_reset_confirm", args=[token]))
            contact_url = request.build_absolute_uri(reverse('quiz:contact'))
            context = {
                "username": user.username,
                "reset_url": reset_url,
                "expiry_minutes": TOKEN_EXPIRY_MINUTES,
                "contact_url": contact_url,
            }
            text_body = render_to_string("quiz/emails/password_reset.txt", context)
            html_body = render_to_string("quiz/emails/password_reset.html", context)
            try:
                msg = EmailMultiAlternatives("Reset your Kids Quiz Game password", text_body, settings.DEFAULT_FROM_EMAIL, [user.email])
                msg.attach_alternative(html_body, "text/html")
                msg.send(fail_silently=False)
            except smtplib.SMTPAuthenticationError as auth_err:
                # SMTP auth failed (bad credentials). Log and attempt to write the email using
                # the file-based backend so the email is preserved for inspection.
                logging.exception("SMTP authentication failed when sending password reset email")
                try:
                    file_conn = get_connection('django.core.mail.backends.filebased.EmailBackend', file_path=settings.EMAIL_FILE_PATH)
                    # send_messages accepts email.message.EmailMessage / EmailMultiAlternatives
                    file_conn.send_messages([msg])
                    messages.error(request, "Email delivery failed (SMTP authentication). A copy was written to disk for inspection.")
                except Exception:
                    logging.exception("Failed to write email to file backend after SMTP auth failure")
                    messages.error(request, "Email delivery failed and could not be saved. Please contact the site administrator.")
                    return render(request, "quiz/password_reset_request.html", {"form": form})
            except Exception:
                # Fall back to send_mail if EmailMultiAlternatives fails for some other reason
                try:
                    send_mail(
                        subject="Reset your Kids Quiz Game password",
                        message=text_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                        html_message=html_body,
                    )
                except Exception:
                    logging.exception("Failed to send password reset email using fallback send_mail")
                    # Try to persist the email to disk as a last resort
                    try:
                        file_conn = get_connection('django.core.mail.backends.filebased.EmailBackend', file_path=settings.EMAIL_FILE_PATH)
                        # Build a simple EmailMultiAlternatives to save
                        saved_msg = EmailMultiAlternatives("Reset your Kids Quiz Game password", text_body, settings.DEFAULT_FROM_EMAIL, [user.email])
                        saved_msg.attach_alternative(html_body, "text/html")
                        file_conn.send_messages([saved_msg])
                        messages.error(request, "Email delivery failed; a copy was written to disk for inspection.")
                    except Exception:
                        logging.exception("Failed to save password reset email to disk")
                        messages.error(request, "Email delivery failed and could not be saved. Please contact the site administrator.")
                        return render(request, "quiz/password_reset_request.html", {"form": form})
            messages.success(request, "Password reset email sent! Please check your inbox and follow the instructions. Go to your email, click the reset link, and set a new password. If you need help, use the Contact Us page.")
            # After successful submission redirect to the "done" page (backwards-compatible name used by tests)
            return redirect("quiz:password_reset_done")
    else:
        form = CustomPasswordResetRequestForm()
    return render(request, "quiz/password_reset_request.html", {"form": form})

def password_reset_confirm(request, token):
    token_data = PASSWORD_RESET_TOKENS.get(token)
    if not token_data:
        messages.error(request, "Invalid or expired password reset link.")
        return render(request, "quiz/password_reset_invalid.html")
    # Check expiry
    created = token_data["created"]
    if timezone.now() - created > datetime.timedelta(minutes=TOKEN_EXPIRY_MINUTES):
        del PASSWORD_RESET_TOKENS[token]
        messages.error(request, "Password reset link has expired.")
        return render(request, "quiz/password_reset_invalid.html")
    user_id = token_data["user_id"]
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return render(request, "quiz/password_reset_invalid.html")
    if request.method == "POST":
        form = CustomSetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["new_password1"]
            user.set_password(password)
            user.save()
            try:
                send_password_reset_confirmation_email(user, request)
            except Exception:
                logging.exception("Unexpected error while sending password reset confirmation email")
            del PASSWORD_RESET_TOKENS[token]
            messages.success(request, "Password reset successful! You can now log in.")
            return redirect("quiz:login")
    else:
        form = CustomSetPasswordForm()
    return render(request, "quiz/password_reset_confirm.html", {"form": form, "token": token, "user": user})

def password_reset_complete(request):
    return render(request, "quiz/password_reset_complete.html")
