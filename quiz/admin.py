from django.contrib import admin

from .models import MathQuestion, QuizSession, UserProgress

admin.site.register(MathQuestion)
admin.site.register(QuizSession)
admin.site.register(UserProgress)
