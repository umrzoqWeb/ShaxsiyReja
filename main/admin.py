# main/admin.py

from django.contrib import admin
from django.conf import settings
from .models import EmployeeActivity, ActivityReview, Reviewer

User = settings.AUTH_USER_MODEL  # ← to'g'ri model

@admin.register(Reviewer)
class ReviewerAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'can_review_employee_taught',
        'can_review_employee_research',
        'can_review_employee_social',
        'can_review_student_taught',
        'can_review_student_research',
        'can_review_student_social',
    )
    list_filter = (
        'can_review_employee_taught',
        'can_review_employee_research',
        'can_review_employee_social',
        'can_review_student_taught',
        'can_review_student_research',
        'can_review_student_social',
    )
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


# CustomUser uchun admin sozlamasi (agar hali qo'shilmagan bo'lsa)
from hemis_oauth.models import CustomUser
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('employee_id',)
    list_filter = UserAdmin.list_filter + ('is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Qo‘shimcha', {'fields': ('employee_id',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Qo‘shimcha', {'fields': ('employee_id',)}),
    )

# Eski ro'yxatni o'chirib, yangisini qo'shish
if admin.site.is_registered(CustomUser):
    admin.site.unregister(CustomUser)
admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(EmployeeActivity)
class EmployeeActivityAdmin(admin.ModelAdmin):
    list_display = ('employee', 'get_activity_type_display', 'status', 'final_points', 'created_at')
    list_filter = ('status', 'activity_type', 'created_at')
    readonly_fields = ('employee', 'assignment', 'activity_type', 'title', 'description', 'evidence_file')


@admin.register(ActivityReview)
class ActivityReviewAdmin(admin.ModelAdmin):
    list_display = ('activity', 'reviewer', 'decision', 'points', 'reviewed_at')
    list_filter = ('decision', 'reviewed_at', 'reviewer')