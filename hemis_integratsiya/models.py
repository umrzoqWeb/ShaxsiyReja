from django.db import models


class Gender(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class AcademicDegree(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class AcademicRank(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class EmploymentForm(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class EmploymentStaff(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class StaffPosition(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class EmployeeStatus(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class EmployeeType(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class StructureType(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class LocalityType(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Department(models.Model):
    id_from_api = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    structure_type = models.ForeignKey(StructureType, on_delete=models.CASCADE)
    locality_type = models.ForeignKey(LocalityType, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    id_from_api = models.IntegerField(unique=True)
    meta_id = models.IntegerField(null=True, blank=True)  # endi keraksiz, lekin qoldirish ham mumkin
    full_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    second_name = models.CharField(max_length=100, blank=True)
    third_name = models.CharField(max_length=100, blank=True)
    employee_id_number = models.CharField(max_length=20, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    birth_date = models.BigIntegerField(null=True, blank=True)
    image = models.URLField(max_length=500, blank=True)
    image_full = models.URLField(max_length=500, blank=True)
    year_of_enter = models.IntegerField(null=True, blank=True)
    specialty = models.CharField(max_length=255, blank=True)
    academic_degree = models.ForeignKey(AcademicDegree, on_delete=models.SET_NULL, null=True, blank=True)
    academic_rank = models.ForeignKey(AcademicRank, on_delete=models.SET_NULL, null=True, blank=True)
    # ⬇️ Quyidagi maydonlar O'CHIRILDI
    # department, staff_position, employment_form, ... — bular endi EmployeeAssignment da
    created_at = models.BigIntegerField(null=True, blank=True)
    updated_at = models.BigIntegerField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name

    def get_category(self):
        """
        Xodimning kategoriyasini quyidagi mantiq bo'yicha qaytaradi:
        1. Agar employment_form.code == "11" bo'lgan tayinlov bo'lsa — shu tayinlov asosida.
        2. Aks holda — faol tayinlovlardan staff_position.code eng kattasini olib, shu bo'yicha.
        """
        # Faqat faol tayinlovlarni olish
        assignments = self.assignments.filter(active=True).select_related(
            'staff_position',
            'employment_form'
        )

        if not assignments.exists():
            return None

        # 1. employment_form.code == "11" bo'lgan tayinlovni qidirish
        primary_assignment = None
        for assign in assignments:
            if assign.employment_form and assign.employment_form.code == "11":
                primary_assignment = assign
                break

        # 2. Agar topilmasa, staff_position.code bo'yicha eng kattasini tanlash
        if primary_assignment is None:
            # Faqat staff_positioni mavjud tayinlovlarni olish
            valid_assignments = [
                a for a in assignments
                if a.staff_position and a.staff_position.code.isdigit()
            ]
            if valid_assignments:
                primary_assignment = max(
                    valid_assignments,
                    key=lambda a: int(a.staff_position.code)
                )
            else:
                return None

        # 3. Kategoriyani aniqlash
        if not primary_assignment.staff_position:
            return None

        code = primary_assignment.staff_position.code
        if code in ['14', '15', '16']:
            return 1
        elif code == '13':
            return 2
        elif code in ['11', '12']:
            return 3
        return None

    @property
    def category_label(self):
        cat = self.get_category()
        return {1: "1-kategoriya", 2: "2-kategoriya", 3: "3-kategoriya"}.get(cat, "Noma'lum")

class EmployeeAssignment(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    meta_id = models.IntegerField()  # HEMISdagi meta ID — har bir ish joyi uchun unikal
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    staff_position = models.ForeignKey(StaffPosition, on_delete=models.SET_NULL, null=True, blank=True)
    employment_form = models.ForeignKey(EmploymentForm, on_delete=models.SET_NULL, null=True, blank=True)
    employment_staff = models.ForeignKey(EmploymentStaff, on_delete=models.SET_NULL, null=True, blank=True)
    employee_status = models.ForeignKey(EmployeeStatus, on_delete=models.SET_NULL, null=True, blank=True)
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.SET_NULL, null=True, blank=True)
    contract_number = models.CharField(max_length=50, blank=True)
    decree_number = models.CharField(max_length=50, blank=True)
    contract_date = models.BigIntegerField(null=True, blank=True)
    decree_date = models.BigIntegerField(null=True, blank=True)
    active = models.BooleanField(default=True)
    hash = models.CharField(max_length=128, blank=True)

    def get_category(self):
        """Xodimning kategoriyasini qaytaradi: 1, 2 yoki 3"""
        if not self.staff_position:
            return None
        code = self.staff_position.code
        if code in ['14', '15', '16']:
            return 1
        elif code == '13':
            return 2
        elif code in ['11', '12']:
            return 3
        return None

    @property
    def category_label(self):
        cat = self.get_category()
        return {1: "1-kategoriya", 2: "2-kategoriya", 3: "3-kategoriya"}.get(cat, "Noma'lum")

    class Meta:
        unique_together = ('employee', 'meta_id')
        verbose_name = "Xodim tayinlovi"
        verbose_name_plural = "Xodim tayinlovlari"

    def __str__(self):
        return f"{self.employee.full_name} — {self.staff_position or 'Lavozimsiz'}"





class Specialty(models.Model):
    id_from_api = models.IntegerField(unique=True)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.code} - {self.name}"

class EducationYear(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=20)
    current = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class EducationType(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class EducationForm(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class MarkingSystem(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    minimum_limit = models.IntegerField()
    count_final_exams = models.IntegerField()
    gpa_limit = models.FloatField()
    updated_at = models.BigIntegerField()  # Unix timestamp

    def __str__(self):
        return self.name

class Curriculum(models.Model):
    id_from_api = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    education_year = models.ForeignKey(EducationYear, on_delete=models.CASCADE)
    education_type = models.ForeignKey(EducationType, on_delete=models.CASCADE)
    education_form = models.ForeignKey(EducationForm, on_delete=models.CASCADE)
    marking_system = models.ForeignKey(MarkingSystem, on_delete=models.CASCADE)
    semester_count = models.IntegerField()
    education_period = models.IntegerField()
    accepted = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    id_from_api = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.code} - {self.name}"

class SubjectType(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class SubjectBlock(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class TrainingType(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ExamType(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class RatingGrade(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    template = models.CharField(max_length=50)
    updated_at = models.BigIntegerField()  # Unix timestamp

    def __str__(self):
        return self.name

class ExamFinish(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Semester(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Many-to-many uchun oraliq modellar
class SubjectDetail(models.Model):
    subject = models.ForeignKey('CurriculumSubject', on_delete=models.CASCADE, related_name='details')
    training_type = models.ForeignKey(TrainingType, on_delete=models.CASCADE)
    academic_load = models.IntegerField()

    def __str__(self):
        return f"{self.training_type.name}: {self.academic_load}"

class SubjectExamType(models.Model):
    subject = models.ForeignKey('CurriculumSubject', on_delete=models.CASCADE, related_name='exam_types')
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    max_ball = models.IntegerField()

    def __str__(self):
        return f"{self.exam_type.name}: {self.max_ball}"

# Asosiy model — bir fan bir o'quv rejada
class CurriculumSubject(models.Model):
    id_from_api = models.IntegerField(unique=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    subject_type = models.ForeignKey(SubjectType, on_delete=models.SET_NULL, null=True, blank=True)
    subject_block = models.ForeignKey(SubjectBlock, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)  # avval yaratilgan
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True)
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, db_column='_curriculum')  # _curriculum → curriculum_id
    rating_grade = models.ForeignKey(RatingGrade, on_delete=models.SET_NULL, null=True, blank=True)
    exam_finish = models.ForeignKey(ExamFinish, on_delete=models.SET_NULL, null=True, blank=True)
    total_acload = models.IntegerField(null=True, blank=True)
    resource_count = models.IntegerField()
    in_group = models.CharField(max_length=100, null=True, blank=True)
    at_semester = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    credit = models.IntegerField()
    created_at = models.BigIntegerField()  # Unix timestamp
    updated_at = models.BigIntegerField()  # Unix timestamp

    def __str__(self):
        return f"{self.subject.name} ({self.semester.name})"

# class Employee(models.Model):
#     id_from_api = models.IntegerField(unique=True)
#     name = models.CharField(max_length=255)
#
#     def __str__(self):
#         return self.name

class Group(models.Model):
    id_from_api = models.IntegerField(unique=True)
    name = models.CharField(max_length=100, blank=True)  # API faqat ID beradi, lekin keyinchalik nom qo'shish mumkin

    def __str__(self):
        return f"{self.name}"

class CurriculumSubjectTeacher(models.Model):
    id_from_api = models.IntegerField(unique=True)
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, db_column='_curriculum')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, db_column='_semester')  # code='11'
    education_year = models.ForeignKey(EducationYear, on_delete=models.CASCADE, db_column='_education_year')  # code='2022'
    department = models.ForeignKey(Department, on_delete=models.CASCADE, db_column='_department')
    training_type = models.ForeignKey(TrainingType, on_delete=models.CASCADE, db_column='_training_type')  # code='11'
    group = models.ForeignKey(Group, on_delete=models.CASCADE, db_column='_group')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    curriculum_subject_detail = models.ForeignKey(SubjectDetail, on_delete=models.CASCADE)  # curriculumSubjectDetail.id → SubjectDetail.id
    students_count = models.IntegerField()
    active = models.BooleanField(default=True)
    created_at = models.BigIntegerField(null=True, blank=True)  # Unix timestamp
    updated_at = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.full_name} — {self.subject.name} (Guruh {self.group.id_from_api})"

class Student(models.Model):
    id_from_api = models.IntegerField(unique=True)
    student_id_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    second_name = models.CharField(max_length=100, blank=True)
    third_name = models.CharField(max_length=100, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    birth_date = models.BigIntegerField(null=True, blank=True)  # Unix timestamp
    image_full = models.URLField(max_length=500, blank=True)
    avg_gpa = models.FloatField(default=0.0)
    avg_grade = models.FloatField(default=0.0)
    student_status = models.ForeignKey('StudentStatus', on_delete=models.SET_NULL, null=True, blank=True)
    education_form = models.ForeignKey('EducationForm', on_delete=models.SET_NULL, null=True, blank=True)
    education_type = models.ForeignKey('EducationType', on_delete=models.SET_NULL, null=True, blank=True)
    specialty = models.ForeignKey('Specialty', on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    level = models.CharField(max_length=50, blank=True)  # "4-kurs"
    semester = models.CharField(max_length=50, blank=True)  # "7-semestr"
    year_of_enter = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.BigIntegerField(null=True, blank=True)
    updated_at = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.full_name

class StudentStatus(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


