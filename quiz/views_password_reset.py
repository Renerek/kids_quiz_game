from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from .forms import CustomPasswordResetRequestForm, CustomSetPasswordForm
import datetime

# In-memory store for tokens (for demo; use a model in production)
PASSWORD_RESET_TOKENS = {}
TOKEN_EXPIRY_MINUTES = 30

def password_reset_request(request):
    if request.method == "POST":
        form = CustomPasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                messages.error(request, "No account found with that email.")
                return render(request, "quiz/password_reset_request.html", {"form": form})
            # Generate token
            token = get_random_string(32)
            PASSWORD_RESET_TOKENS[token] = {
                "user_id": user.id,
                "created": timezone.now(),
            }
            reset_url = request.build_absolute_uri(reverse("quiz:password_reset_confirm", args=[token]))
            contact_url = request.build_absolute_uri(reverse('quiz:contact'))
            html_message = (
                f"Hi {user.username},<br><br>"
                "We received a request to reset your password for Kids Quiz Game.<br><br>"
                f"To reset your password, please click <a href=\"{reset_url}\">this link</a> (valid for {TOKEN_EXPIRY_MINUTES} minutes).<br><br>"
                "If you did not request this, you can ignore this email.<br><br>"
                f"Need help or have questions? <a href=\"{contact_url}\">Contact us</a>.<br><br>"
                "Best wishes,<br>The Kids Quiz Game Team"
            )
            send_mail(
                subject="Reset your Kids Quiz Game password",
                message=(
                    f"Hi {user.username},\n\n"
                    "We received a request to reset your password for Kids Quiz Game.\n\n"
                    f"To reset your password, please use this link (valid for {TOKEN_EXPIRY_MINUTES} minutes): {reset_url}\n\n"
                    "If you did not request this, you can ignore this email.\n\n"
                    f"Need help or have questions? Contact us: {contact_url}\n\n"
                    "Best wishes,\nThe Kids Quiz Game Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
                html_message=html_message,
            )
            messages.success(request, "Password reset email sent! Please check your inbox and follow the instructions. Go to your email, click the reset link, and set a new password. If you need help, use the Contact Us page.")
            return redirect("quiz:password_reset_request")
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
            del PASSWORD_RESET_TOKENS[token]
            messages.success(request, "Password reset successful! You can now log in.")
            return redirect("quiz:login")
    else:
        form = CustomSetPasswordForm()
    return render(request, "quiz/password_reset_confirm.html", {"form": form, "token": token, "user": user})

def password_reset_complete(request):
    return render(request, "quiz/password_reset_complete.html")
