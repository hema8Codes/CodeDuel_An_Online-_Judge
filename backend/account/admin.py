from django.contrib import admin
from .models import UserProfile, UserBioProfileForDisplay, UserToken, Reset

admin.site.register(UserToken)
admin.site.register(Reset)
admin.site.register(UserProfile)
admin.site.register(UserBioProfileForDisplay)


