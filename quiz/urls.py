from django.urls import path

from . import views

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
]
