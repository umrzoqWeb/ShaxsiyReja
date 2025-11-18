from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     list_display = ("username", "email", "first_name", "last_name", "employee_id", "is_staff", "is_active")
#     fieldsets = UserAdmin.fieldsets + (
#         (None, {"fields": ("employee_id",)}),
#     )
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         (None, {"fields": ("employee_id",)}),
#     )
#
# admin.site.register(CustomUser, CustomUserAdmin)
