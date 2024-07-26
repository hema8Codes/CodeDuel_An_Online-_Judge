from django.db import models
from django.contrib.auth.models import User


class UserToken(models.Model):
    user_id = models.IntegerField()
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()
    

class Reset(models.Model):
    email = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='userprofile', on_delete=models.CASCADE)
    resume = models.FileField(null=True, upload_to='resumes/')
    
    def __str__(self):
        return f"Profile for {self.user.email}"

class UserBioProfileForDisplay(models.Model):
    user = models.OneToOneField(User, related_name='userbioprofile', on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='images/')
    bio_about = models.TextField(max_length=300)
    
    @property
    def display_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def __str__(self):
        return self.display_name
    
    

