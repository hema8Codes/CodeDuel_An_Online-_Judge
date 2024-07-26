from django.contrib import admin
from .models import Problems, Submission, TestCase, Tags

# Register your models here.
admin.site.register(Problems)
admin.site.register(Submission)
admin.site.register(TestCase)
admin.site.register(Tags)