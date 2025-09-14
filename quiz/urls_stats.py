from django.urls import path
from . import views_stats

app_name = "quiz"

urlpatterns = [
    # ...existing urls...
    path('stats/', views_stats.user_stats, name='user_stats'),
]
