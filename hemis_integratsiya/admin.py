from django.contrib import admin
from django.contrib import messages
from django.urls import path, reverse
from django.shortcuts import redirect
from .models import *
from .utils import fetch_and_save_students

#
# Umumiy admin sinf — kerak bo'lsa kengaytirish mumkin
class BaseAdmin(admin.ModelAdmin):
    save_on_top = True
    list_per_page = 20
#
# # 1. StructureType
# @admin.register(StructureType)
# class StructureTypeAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#     search_fields = ('code', 'name')
#
# # 2. LocalityType
# @admin.register(LocalityType)
# class LocalityTypeAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#     search_fields = ('code', 'name')
#
# # 3. Department
# @admin.register(Department)
# class DepartmentAdmin(BaseAdmin):
#     list_display = ('id_from_api', 'name', 'code', 'structure_type', 'locality_type', 'active')
#     list_filter = ('active', 'structure_type', 'locality_type')
#     search_fields = ('name', 'code')
#     list_editable = ('active',)
#
# # 4. Specialty
# @admin.register(Specialty)
# class SpecialtyAdmin(BaseAdmin):
#     list_display = ('id_from_api', 'code', 'name')
#     search_fields = ('code', 'name')
#     list_display_links = ('code', 'name')
#
# # 5. EducationYear
# @admin.register(EducationYear)
# class EducationYearAdmin(BaseAdmin):
#     list_display = ('code', 'name', 'current')
#     list_filter = ('current',)
#     list_editable = ('current',)
#
# # 6. EducationType
# @admin.register(EducationType)
# class EducationTypeAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#     search_fields = ('name',)
#
# # 7. EducationForm
# @admin.register(EducationForm)
# class EducationFormAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#     search_fields = ('name',)
#
# # 8. MarkingSystem
# @admin.register(MarkingSystem)
# class MarkingSystemAdmin(BaseAdmin):
#     list_display = ('code', 'name', 'minimum_limit', 'count_final_exams', 'gpa_limit')
#     search_fields = ('name', 'code')
#
# # 9. Curriculum (asosiy model)
# @admin.register(Curriculum)
# class CurriculumAdmin(BaseAdmin):
#     list_display = (
#         'id_from_api',
#         'name',
#         'specialty',
#         'department',
#         'education_year',
#         'education_type',
#         'education_form',
#         'semester_count',
#         'active',
#         'accepted'
#     )
#     list_filter = (
#         'active',
#         'accepted',
#         'education_year',
#         'education_type',
#         'education_form',
#         'department'
#     )
#     search_fields = ('name', 'specialty__name', 'specialty__code')
#     list_editable = ('active', 'accepted')
#     readonly_fields = ('id_from_api',)
#
#     # Sinxronizatsiya tugmasi uchun URL qo'shish (avvalgi qismda qilingani kabi)
#     def get_urls(self):
#         from django.urls import path
#         from django.shortcuts import redirect
#         from django.contrib import messages
#         from .utils import fetch_and_save_curricula
#
#         urls = super().get_urls()
#         custom_urls = [
#             path('sync/', self.admin_site.admin_view(self.sync_view), name='hemis_integratsiya_curriculum_sync'),
#         ]
#         return custom_urls + urls
#
#     def sync_view(self, request):
#         try:
#             from .utils import fetch_and_save_curricula
#             fetch_and_save_curricula()
#             messages.success(request, "✅ Ma'lumotlar tashqi API'dan muvaffaqiyatli yangilandi!")
#         except Exception as e:
#             messages.error(request, f"❌ Xatolik: {str(e)}")
#         from django.urls import reverse
#         return redirect(reverse('admin:hemis_integratsiya_curriculum_changelist'))
#
#     def changelist_view(self, request, extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['sync_url'] = 'admin:hemis_integratsiya_curriculum_sync'
#         return super().changelist_view(request, extra_context=extra_context)
#
#
#
# @admin.register(Subject)
# class SubjectAdmin(BaseAdmin):
#     list_display = ('id_from_api', 'code', 'name')
#     search_fields = ('code', 'name')
#
# @admin.register(SubjectType)
# class SubjectTypeAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#
# @admin.register(SubjectBlock)
# class SubjectBlockAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#
# @admin.register(TrainingType)
# class TrainingTypeAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#
# @admin.register(ExamType)
# class ExamTypeAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#
# @admin.register(RatingGrade)
# class RatingGradeAdmin(BaseAdmin):
#     list_display = ('code', 'name', 'template')
#
# @admin.register(ExamFinish)
# class ExamFinishAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#
# @admin.register(Semester)
# class SemesterAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#
# # Inline modellar — tafsilotlarni asosiy sahifada ko'rsatish uchun
# class SubjectDetailInline(admin.TabularInline):
#     model = SubjectDetail
#     extra = 0
#
# class SubjectExamTypeInline(admin.TabularInline):
#     model = SubjectExamType
#     extra = 0
#
# @admin.register(CurriculumSubject)
# class CurriculumSubjectAdmin(BaseAdmin):
#     list_display = (
#         'id','id_from_api', 'subject', 'curriculum', 'semester',
#         'credit', 'total_acload', 'active'
#     )
#     list_filter = ('active', 'semester', 'curriculum__department')
#     search_fields = ('subject__name', 'subject__code', 'curriculum__name')
#     inlines = [SubjectDetailInline, SubjectExamTypeInline]
#
#     def get_urls(self):
#         from django.urls import path
#         urls = super().get_urls()
#         custom_urls = [
#             path('sync/', self.admin_site.admin_view(self.sync_subjects_view), name='hemis_integratsiya_curriculumsubject_sync'),
#         ]
#         return custom_urls + urls
#
#     def sync_subjects_view(self, request):
#         try:
#             from .utils import fetch_and_save_curriculum_subjects
#             fetch_and_save_curriculum_subjects()
#             messages.success(request, "✅ Fanlar ro'yxati muvaffaqiyatli yangilandi!")
#         except Exception as e:
#             messages.error(request, f"❌ Xatolik: {str(e)}")
#         return redirect(reverse('admin:hemis_integratsiya_curriculumsubject_changelist'))
#
#     def changelist_view(self, request, extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['sync_url'] = 'admin:hemis_integratsiya_curriculumsubject_sync'
#         return super().changelist_view(request, extra_context=extra_context)
#
#
#
# @admin.register(Group)
# class GroupAdmin(BaseAdmin):
#     list_display = ('id_from_api', 'name')
#     search_fields = ('name', 'id_from_api')
#
#     def get_urls(self):
#         from django.urls import path
#         urls = super().get_urls()
#         custom_urls = [
#             path('sync/', self.admin_site.admin_view(self.sync_groups_view), name='hemis_integratsiya_group_sync'),
#         ]
#         return custom_urls + urls
#
#     def sync_groups_view(self, request):
#         try:
#             from .utils import fetch_and_save_groups
#             fetch_and_save_groups()
#             messages.success(request, "✅ Guruhlar ro'yxati muvaffaqiyatli yangilandi!")
#         except Exception as e:
#             messages.error(request, f"❌ Xatolik: {str(e)}")
#         return redirect(reverse('admin:hemis_integratsiya_group_changelist'))
#
#     def changelist_view(self, request, extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['sync_url'] = 'admin:hemis_integratsiya_group_sync'
#         return super().changelist_view(request, extra_context=extra_context)
#
# @admin.register(CurriculumSubjectTeacher)
# class CurriculumSubjectTeacherAdmin(BaseAdmin):
#     list_display = (
#         'id_from_api',
#         'employee',
#         'subject',
#         'group',
#         'students_count',
#         'active'
#     )
#     list_filter = ('active', 'semester', 'education_year', 'department')
#     search_fields = ('employee__full_name', 'subject__name', 'group__id_from_api')
#
#     def get_urls(self):
#         from django.urls import path
#         urls = super().get_urls()
#         custom_urls = [
#             path('sync/', self.admin_site.admin_view(self.sync_teachers_view), name='hemis_integratsiya_curriculumsubjectteacher_sync'),
#         ]
#         return custom_urls + urls
#
#     def sync_teachers_view(self, request):
#         try:
#             from .utils import fetch_and_save_curriculum_subject_teachers
#             fetch_and_save_curriculum_subject_teachers()
#             messages.success(request, "✅ O'qituvchilar ro'yxati muvaffaqiyatli yangilandi!")
#         except Exception as e:
#             messages.error(request, f"❌ Xatolik: {str(e)}")
#         return redirect(reverse('admin:hemis_integratsiya_curriculumsubjectteacher_changelist'))
#
#     def changelist_view(self, request, extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['sync_url'] = 'admin:hemis_integratsiya_curriculumsubjectteacher_sync'
#         return super().changelist_view(request, extra_context=extra_context)
#
#
# @admin.register(Gender)
# class GenderAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#
# @admin.register(AcademicDegree)
# class AcademicDegreeAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#
# @admin.register(AcademicRank)
# class AcademicRankAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#
# @admin.register(EmploymentForm)
# class EmploymentFormAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#
# @admin.register(EmploymentStaff)
# class EmploymentStaffAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#
# @admin.register(StaffPosition)
# class StaffPositionAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#
# @admin.register(EmployeeStatus)
# class EmployeeStatusAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#
# @admin.register(EmployeeType)
# class EmployeeTypeAdmin(BaseAdmin):
#     list_display = ('code', 'name')
#
#
#
#
class EmployeeAssignmentInline(admin.TabularInline):
    model = EmployeeAssignment
    extra = 0
    fields = (
        'meta_id', 'department', 'staff_position', 'employment_form',
        'employment_staff', 'employee_status', 'employee_type',
        'contract_number', 'contract_date', 'active'
    )
    readonly_fields = ('meta_id',)


@admin.register(Employee)
class EmployeeAdmin(BaseAdmin):
    list_display = ('id_from_api', 'full_name', 'employee_id_number', 'active')
    list_filter = ('active', 'academic_degree', 'academic_rank')
    search_fields = ('full_name', 'short_name', 'employee_id_number')
    list_editable = ('active',)
    inlines = [EmployeeAssignmentInline]  # ← yangi qator

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('sync/', self.admin_site.admin_view(self.sync_employees_view), name='hemis_integratsiya_employee_sync'),
        ]
        return custom_urls + urls

    def sync_employees_view(self, request):
        try:
            from .utils import fetch_and_save_employees
            fetch_and_save_employees()
            messages.success(request, "✅ Xodimlar va ularning tayinlovlari muvaffaqiyatli yangilandi!")
        except Exception as e:
            messages.error(request, f"❌ Xatolik: {str(e)}")
        return redirect(reverse('admin:hemis_integratsiya_employee_changelist'))

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['sync_url'] = 'admin:hemis_integratsiya_employee_sync'
        return super().changelist_view(request, extra_context=extra_context)


# @admin.register(EmployeeAssignment)
# class EmployeeAssignmentAdmin(BaseAdmin):
#     list_display = (
#         'employee', 'meta_id', 'department', 'staff_position',
#         'employment_form', 'active'
#     )
#     list_filter = ('active', 'department', 'staff_position', 'employment_form')
#     search_fields = ('employee__full_name', 'employee__employee_id_number')
#     list_editable = ('active',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    change_list_template = 'admin/hemis_integratsiya/student/change_list.html'
    list_display = ('id_from_api', 'full_name', 'student_id_number', 'group', 'active')
    list_filter = ('active', 'education_type', 'department')
    search_fields = ('full_name', 'student_id_number')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('sync-students/', self.admin_site.admin_view(self.sync_students), name='hemis_integratsiya_sync_students'),
        ]
        return custom_urls + urls

    def sync_students(self, request):
        try:
            fetch_and_save_students()
            messages.success(request, "✅ Talabalar ro'yxati muvaffaqiyatli yangilandi!")
        except Exception as e:
            messages.error(request, f"❌ Xatolik: {str(e)}")
        return redirect(reverse('admin:hemis_integratsiya_student_changelist'))

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['sync_url'] = 'admin:hemis_integratsiya_sync_students'
        return super().changelist_view(request, extra_context=extra_context)