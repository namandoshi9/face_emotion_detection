from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=100)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=(('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')), blank=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True,null=True)

class EmotionDetection(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True,null=True)
    date = models.DateTimeField(auto_now_add=True)
    happy = models.FloatField(default=0)
    anger = models.FloatField(default=0)
    surprise = models.FloatField(default=0)
    neutral = models.FloatField(default=0)
    fear = models.FloatField(default=0)
    sad = models.FloatField(default=0)

    def __str__(self):
        return f"Emotion Detection Result on {self.date}"
    