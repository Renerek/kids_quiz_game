from django.contrib.auth.models import User
from django.db import models


class MathQuestion(models.Model):
    QUESTION_TYPES = [
        ("add", "Addition"),
        ("sub", "Subtraction"),
        ("mul", "Multiplication"),
        ("div", "Division"),
    ]
    question_text = models.CharField(max_length=100)
    answer = models.IntegerField()
    type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    difficulty = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question_text} (Level {self.difficulty})"


class QuizSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    highest_level = models.IntegerField(default=1)
    last_played = models.DateTimeField(auto_now=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(null=True, blank=True)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile for {self.user.username}"
