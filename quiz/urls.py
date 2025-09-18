from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views


from . import views
from .views_mixed import mixed_game

app_name = "quiz"

urlpatterns = [
    path("", views.home, name="home"),
    path("start/", views.start_quiz, name="start"),
    path("question/", views.question, name="question"),
    path("submit/", views.submit_answer, name="submit_answer"),
    path("spelling/", views.spelling_game, name="spelling"),
    path("what-time/", views.what_time_is_it, name="what_time"),
    path("basic-questions/", views.basic_questions, name="basic_questions"),
    path("colors-shapes/", views.colors_shapes, name="colors_shapes"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout, name="logout"),
    path("verify/<str:token>/", views.verify_email, name="verify_email"),
    path("resend-verification/", views.resend_verification, name="resend_verification"),
    # Custom password reset flow
    path("password-reset/", __import__('quiz.views_password_reset').views_password_reset.password_reset_request, name="password_reset_request"),
    # Backwards-compatible alias used by tests and older code
    path("password-reset/", __import__('quiz.views_password_reset').views_password_reset.password_reset_request, name="password_reset"),
    path("password-reset/confirm/<str:token>/", __import__('quiz.views_password_reset').views_password_reset.password_reset_confirm, name="password_reset_confirm"),
    path("password-reset/complete/", __import__('quiz.views_password_reset').views_password_reset.password_reset_complete, name="password_reset_complete"),
    # Backwards-compatible names for password reset flow
    path("password-reset/done/", __import__('quiz.views_password_reset').views_password_reset.password_reset_complete, name="password_reset_done"),
    path("animals-game/", views.animals_game, name="animals_game"),
    path("general-knowledge/", views.general_knowledge_game, name="general_knowledge_game"),
    path("fruits-game/", views.fruits_game, name="fruits_game"),
    path("mixed-game/", mixed_game, name="mixed_game"),
    path("stats/", __import__('quiz.views_stats').views_stats.user_stats, name="user_stats"),
    path("profile/", views.profile, name="profile"),
    path("update-account/", views.update_account, name="update_account"),
    path("settings/", views.settings_view, name="settings"),
]
