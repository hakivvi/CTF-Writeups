from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class WebFramework(models.Model):
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    icon = models.URLField(max_length=500)

    def __str__(self):
        return f"{self.name} ({self.type})"


class Experience(models.Model):

    MAX_TEXT_LENGTH = 500

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="experiences")
    web_framework = models.ForeignKey(WebFramework, on_delete=models.CASCADE, related_name="experiences")
    text = models.CharField(max_length=MAX_TEXT_LENGTH)
    hot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Experience by {self.owner.username} on {self.web_framework.name}"

    class Meta:
        ordering = ['-hot', '-created_at']
