
from django.contrib.auth.models import User
from django.db import models

class UserStat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.CharField(max_length=50)  # e.g., 'math', 'spelling', 'animals', etc.
    score = models.IntegerField(default=0)
    correct = models.IntegerField(default=0)
    incorrect = models.IntegerField(default=0)
    time_spent = models.FloatField(default=0.0)  # seconds
    played_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.game} on {self.played_at:%Y-%m-%d %H:%M}" 


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
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    age_group = models.CharField(max_length=20, blank=True, choices=[
        ("3-5", "3-5 years"),
        ("6-8", "6-8 years"),
        ("9-12", "9-12 years"),
        ("other", "Other")
    ])
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    theme = models.CharField(max_length=20, blank=True, choices=[
        ("light", "Light"),
        ("dark", "Dark"),
        ("forest", "Forest"),
        ("ocean", "Ocean"),
        ("space", "Space")
    ], default="light")
    sound_music = models.BooleanField(default=True)
    sound_voice = models.BooleanField(default=True)
    language = models.CharField(max_length=20, blank=True, default="en")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile for {self.user.username}"
