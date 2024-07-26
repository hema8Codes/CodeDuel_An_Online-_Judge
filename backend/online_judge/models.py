from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Problems(models.Model):
    LANGUAGE_CHOICES = [
        ("C++", "C++"),
        ("Python", "Python"),
    ]

    problem_name = models.CharField(max_length=255)
    statement_description = models.TextField(max_length=2000)
    problem_visualization_illustration = models.ImageField(upload_to='images/problems', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    difficulty = models.CharField(
        max_length=20,
        blank=True,
        choices=[("Hard", "Hard"), ("Easy", "Easy"), ("Medium", "Medium")],
    )
    language = models.CharField(
        max_length=20,
        blank=True,
        choices=LANGUAGE_CHOICES
    )
    constraint_description = models.TextField(max_length=500, default='')

    def __str__(self):
        return self.problem_name

class TestCase(models.Model):
    problem = models.ForeignKey(Problems, on_delete=models.CASCADE)
    input = models.TextField()  
    output = models.TextField()  

    def __str__(self):
        return f"Test case for {self.problem.problem_name}"


class Tags(models.Model):
    problem = models.ForeignKey(Problems, on_delete=models.CASCADE)
    tag_name = models.CharField(max_length=255)

    def __str__(self):
        return self.tag_name

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problems, on_delete=models.CASCADE)
    language = models.CharField(
        max_length=20,
        blank=True,
        choices=[("C++", "C++"), ("Python", "Python")]
    )
    verdict = models.TextField() 
    compiler_output = models.TextField(max_length=100000)
    test_case_results = models.JSONField()
    submitted_code = models.TextField(max_length=100000)
    submitted_at = models.DateTimeField(auto_now_add=True)
    execution_time = models.BigIntegerField(validators=[MinValueValidator(0)])  # Can be large
    memory_used = models.BigIntegerField()  # Changed to BigIntegerField to allow negative numbers

    def __str__(self):
        return f"Submission by {self.user.username} on {self.submitted_at}"