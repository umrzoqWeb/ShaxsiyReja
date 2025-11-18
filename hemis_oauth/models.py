from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('employee', 'Xodim'),
        ('student', 'Talaba'),
    ]

    user_type = models.CharField("Foydalanuvchi turi", max_length=10, choices=USER_TYPE_CHOICES)
    employee_id = models.IntegerField("Xodim ID", null=True, blank=True, unique=True)
    student_id = models.CharField("Talaba ID", max_length=20, null=True, blank=True, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['employee_id'],
                name='unique_employee_id',
                condition=models.Q(employee_id__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['student_id'],
                name='unique_student_id',
                condition=models.Q(student_id__isnull=False)
            ),
        ]