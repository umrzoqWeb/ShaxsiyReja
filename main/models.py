# models.py
from django.db import models
from hemis_integratsiya.models import Employee, EmployeeAssignment
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class EmployeeActivity(models.Model):
    """
    Xodim tomonidan yuklangan faoliyat (har bir mezon uchun alohida yozuv)
    """
    ACTIVITY_TYPE_CHOICES = [
        # --- 1-kategoriya (Dotsent, Professor, Kafedra mudiri) ---
        ('textbook', 'Darslik'),
        ('manual', 'O‘quv/kl. qo‘llanma'),
        ('mobility', 'Akademik mobilnost'),
        ('method_guide', 'O‘quv-uslubiy tavsiyanoma'),
        ('teaching_quality', 'Ta’lim sifati'),
        ('patent', 'Ixtiroga patent'),
        ('project', 'Xalqaro/Respublika loyihasi'),
        ('phd_supervision', 'PhD/DSc rahbarlik'),
        ('diss_defense', 'Dissertatsiya himoyasi'),
        ('monograph', 'Monografiya'),
        ('scopus', 'Scopus maqola'),
        ('wos', 'Web of Science'),
        ('oak', 'OAK jurnal'),
        ('olympiad_mentor', 'Olimpiada/tanlov rahbari'),
        # --- 2- va 3-kategoriyalar uchun umumiy ---
        ('creative_circle', 'Ijodiy/sport to‘garak'),
        ('media', 'OAVda ishtirok'),
        ('personal_plan', 'Shaxsiy ish rejasi'),
        ('discipline', 'Ijro intizomi'),
        # --- 3-kategoriya uchun maxsus ---
        ('phd_topic_approval', 'PhD mavzusini tasdiqlash'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Jarayonda'),
        ('approved', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Xodim")
    assignment = models.ForeignKey(EmployeeAssignment, on_delete=models.CASCADE, verbose_name="Tayinlov")
    activity_type = models.CharField("Mezon turi", max_length=50, choices=ACTIVITY_TYPE_CHOICES)
    title = models.CharField("Hujjat nomi", max_length=255)
    description = models.TextField("Izoh", blank=True)
    evidence_file = models.FileField("Fayl", upload_to='evidence/%Y/%m/', blank=True, null=True)

    # Yakuniy holat — barcha tekshiruvchilar javob bergandan keyin
    status = models.CharField("Holat", max_length=20, choices=STATUS_CHOICES, default='pending')
    final_points = models.FloatField("Yakuniy ball (o'rtacha)", default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.full_name} — {self.get_activity_type_display()}"

    class Meta:
        verbose_name = "Xodim faoliyati"
        verbose_name_plural = "Xodim faoliyatlari"


class ActivityReview(models.Model):
    activity = models.ForeignKey(
        'EmployeeActivity',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← to'g'ri model
        on_delete=models.CASCADE,
        verbose_name="Tekshiruvchi"
    )
    decision = models.CharField(
        max_length=10,
        choices=[('approve', 'Tasdiqlash'), ('reject', 'Rad etish')]
    )
    comment = models.TextField("Izoh (rad etishda)", blank=True)
    points = models.FloatField("Berilgan ball", default=0.0)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('activity', 'reviewer')

class Reviewer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Foydalanuvchi"
    )
    # Xodimlar uchun
    can_review_employee_taught = models.BooleanField("Xodimlar: Ta'limni tekshiradi", default=False)
    can_review_employee_research = models.BooleanField("Xodimlar: Ilmiy ishlarni tekshiradi", default=False)
    can_review_employee_social = models.BooleanField("Xodimlar: Ijtimoiy ishlarni tekshiradi", default=False)

    # Talabalar uchun
    can_review_student_taught = models.BooleanField("Talabalar: Ta'limni tekshiradi", default=False)
    can_review_student_research = models.BooleanField("Talabalar: Ilmiy ishlarni tekshiradi", default=False)
    can_review_student_social = models.BooleanField("Talabalar: Ijtimoiy ishlarni tekshiradi", default=False)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} — Tekshiruvchi"

    class Meta:
        verbose_name = "Tekshiruvchi"
        verbose_name_plural = "Tekshiruvchilar"


class StudentActivity(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        # 1. Ta'lim faoliyati
        ('attendance', 'Dars mashg‘ulotlariga davomati'),
        ('grades', 'Fanlarni o‘zlashtirishi (a‘lo baholarda)'),
        ('student_mobility', 'Akademik mobiligi'),
        ('circle_participation', 'To‘garaklarda ishtirok etishi'),

        # 2. Ilmiy-innovatsion
        ('student_oak', 'OAK jurnalida maqola'),
        ('olympiad_award', 'Fan olimpiadasida sovrin'),
        ('language_cert', 'Chet tili sertifikati'),

        # 3. Ijtimoiy-ma’naviy
        ('moral_events', 'Ma‘naviy-ma‘rifiy tadbirlarda ishtirok'),
        ('initiative_award', '“5 tashabbus”, tanlovda ishtirok'),
        ('social_media', 'Ijtimoiy tarmoqlardagi faollik'),
    ]

    STUDENT_SECTION_CHOICES = [
        ('taught', 'Ta’lim faoliyati'),
        ('research', 'Ilmiy-innovatsion faoliyat'),
        ('social', 'Ijtimoiy, ma’naviy-ma’rifiy faollik'),
    ]

    student = models.ForeignKey('hemis_integratsiya.Student', on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPE_CHOICES)
    section = models.CharField(max_length=20, choices=STUDENT_SECTION_CHOICES)

    # Faqat "Hujjat yuklanadi" bo'lgan mezonlar uchun
    title = models.CharField("Hujjat nomi", max_length=255, blank=True)
    description = models.TextField("Izoh", blank=True)
    evidence_file = models.FileField("Fayl", upload_to='student_evidence/%Y/%m/', blank=True, null=True)

    # Hamma mezonlar uchun
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Jarayonda'),
        ('approved', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
    ], default='pending')
    final_points = models.FloatField("Yakuniy ball", default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def requires_document(self):
        """Hujjat talab qilinadimi?"""
        return self.activity_type in [
            'student_mobility',
            'student_oak',
            'olympiad_award',
            'language_cert',
            'initiative_award',
        ]

    def __str__(self):
        return f"{self.student.full_name} — {self.get_activity_type_display()}"


class StudentReview(models.Model):
    activity = models.ForeignKey(
        StudentActivity,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Tekshiruvchi"
    )
    decision = models.CharField(
        max_length=10,
        choices=[('approve', 'Tasdiqlash'), ('reject', 'Rad etish')],
        default='approve'
    )
    comment = models.TextField("Izoh (rad etishda)", blank=True)
    points = models.FloatField("Berilgan ball", default=0.0)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('activity', 'reviewer')