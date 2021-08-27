from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import BloodTestResults
from .models import User

admin.site.register(User, UserAdmin)


@admin.register(BloodTestResults)
class BloodTestResultAdmin(admin.ModelAdmin):
    list_display = ["user", "timestamp"]
