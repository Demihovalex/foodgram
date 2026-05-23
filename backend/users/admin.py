from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "email", "username", "first_name", "last_name")
    search_fields = ("email", "username")
    list_filter = ("is_active", "is_staff")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("username",
         "first_name", "last_name", "avatar")}),
        ("Permissions", {"fields": ("is_active", "is_staff",
         "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "first_name",
                       "last_name", "password1", "password2"),
        }),
    )
