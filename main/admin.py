from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import BloodTestResults, CustomToken, Lab, User

admin.site.register(User, UserAdmin)


@admin.register(BloodTestResults)
class BloodTestResultAdmin(admin.ModelAdmin):
    list_display = ("user", "timestamp", "results", "ready", "lab")


@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "address",
        "address_2",
        "city",
        "post_code",
        "country",
        "email",
        "number",
    )


@admin.register(CustomToken)
class CustomTokenAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "user",
        "name",
    )
