import requests
from django.utils import timezone
from .models import *
import logging

logger = logging.getLogger(__name__)

API_URL = "https://student.zarmeduniver.com/rest/v1/data/curriculum-list"
API_SUBJECT_URL = "https://student.zarmeduniver.com/rest/v1/data/curriculum-subject-list"
API_TEACHER_URL = "https://student.zarmeduniver.com/rest/v1/data/curriculum-subject-teacher-list"
API_EMPLOYEE_URL = "https://student.zarmeduniver.com/rest/v1/data/employee-list"
API_GROUP_URL = "https://student.zarmeduniver.com/rest/v1/data/group-list"
API_STUDENT_URL = "https://student.zarmeduniver.com/rest/v1/data/student-list"

HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer cC2jZGCaKUpffoWe542NLao7DNkyRka_"
}

def fetch_and_save_curricula():
    page = 1
    total_pages = 1  # boshlang'ich qiymat

    while page <= total_pages:
        params = {"limit": 200, "page": page}
        response = requests.get(API_URL, headers=HEADERS, params=params)
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code}")

        data = response.json()
        items = data["data"]["items"]
        total_pages = data["data"]["pagination"]["pageCount"]

        for item in items:
            # Specialty
            specialty_data = item["specialty"]
            specialty, _ = Specialty.objects.update_or_create(
                id_from_api=specialty_data["id"],
                defaults={
                    "code": specialty_data["code"],
                    "name": specialty_data["name"]
                }
            )

            # StructureType
            st_data = item["department"]["structureType"]
            structure_type, _ = StructureType.objects.get_or_create(
                code=st_data["code"],
                defaults={"name": st_data["name"]}
            )

            # LocalityType
            lt_data = item["department"]["localityType"]
            locality_type, _ = LocalityType.objects.get_or_create(
                code=lt_data["code"],
                defaults={"name": lt_data["name"]}
            )

            # Department
            dept_data = item["department"]
            department, _ = Department.objects.update_or_create(
                id_from_api=dept_data["id"],
                defaults={
                    "name": dept_data["name"],
                    "code": dept_data["code"],
                    "structure_type": structure_type,
                    "locality_type": locality_type,
                    "active": dept_data["active"]
                }
            )

            # EducationYear
            ey_data = item["educationYear"]
            education_year, _ = EducationYear.objects.update_or_create(
                code=ey_data["code"],
                defaults={
                    "name": ey_data["name"],
                    "current": ey_data["current"]
                }
            )

            # EducationType
            et_data = item["educationType"]
            education_type, _ = EducationType.objects.update_or_create(
                code=et_data["code"],
                defaults={"name": et_data["name"]}
            )

            # EducationForm
            ef_data = item["educationForm"]
            education_form, _ = EducationForm.objects.update_or_create(
                code=ef_data["code"],
                defaults={"name": ef_data["name"]}
            )

            # MarkingSystem
            ms_data = item["markingSystem"]
            marking_system, _ = MarkingSystem.objects.update_or_create(
                code=ms_data["code"],
                defaults={
                    "name": ms_data["name"],
                    "minimum_limit": ms_data["minimum_limit"],
                    "count_final_exams": ms_data["count_final_exams"],
                    "gpa_limit": ms_data["gpa_limit"],
                    "updated_at": ms_data["updated_at"]
                }
            )

            # Curriculum
            Curriculum.objects.update_or_create(
                id_from_api=item["id"],
                defaults={
                    "name": item["name"],
                    "specialty": specialty,
                    "department": department,
                    "education_year": education_year,
                    "education_type": education_type,
                    "education_form": education_form,
                    "marking_system": marking_system,
                    "semester_count": item["semester_count"],
                    "education_period": item["education_period"],
                    "accepted": item["accepted"],
                    "active": item["active"]
                }
            )

        page += 1


def fetch_and_save_curriculum_subjects():
    page = 1
    total_pages = 1

    while page <= total_pages:
        params = {"limit": 200, "page": page}
        try:
            response = requests.get(API_SUBJECT_URL, headers=HEADERS, params=params, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"API so'rovi xatolikka uchradi (sahifa {page}): {e}")
            raise Exception(f"API so'rovi amalga oshmadi: {e}")

        data = response.json()
        items = data.get("data", {}).get("items", [])
        total_pages = data.get("data", {}).get("pagination", {}).get("pageCount", 1)

        for item in items:
            try:
                # === 1. Subject (majburiy) ===
                subj_data = item.get("subject")
                if not subj_data:
                    logger.warning(f"O'tkazib yuborildi: subject yo'q, API id={item.get('id')}")
                    continue
                subject, _ = Subject.objects.update_or_create(
                    id_from_api=subj_data["id"],
                    defaults={"name": subj_data.get("name", ""), "code": subj_data.get("code", "")}
                )

                # === 2. SubjectType ===
                st_data = item.get("subjectType")
                subject_type = None
                if st_data:
                    subject_type, _ = SubjectType.objects.update_or_create(
                        code=st_data.get("code", ""),
                        defaults={"name": st_data.get("name", "")}
                    )

                # === 3. SubjectBlock ===
                sb_data = item.get("subjectBlock")
                subject_block = None
                if sb_data:
                    subject_block, _ = SubjectBlock.objects.update_or_create(
                        code=sb_data.get("code", ""),
                        defaults={"name": sb_data.get("name", "")}
                    )

                # === 4. Department ===
                dept_data = item.get("department")
                if not dept_data:
                    logger.warning(f"O'tkazib yuborildi: department yo'q, subject id={item.get('id')}")
                    continue

                # StructureType
                struct_type = None
                struct_type_data = dept_data.get("structureType")
                if struct_type_data:
                    struct_type, _ = StructureType.objects.get_or_create(
                        code=struct_type_data.get("code", ""),
                        defaults={"name": struct_type_data.get("name", "")}
                    )

                # LocalityType
                loc_type = None
                loc_type_data = dept_data.get("localityType")
                if loc_type_data:
                    loc_type, _ = LocalityType.objects.get_or_create(
                        code=loc_type_data.get("code", ""),
                        defaults={"name": loc_type_data.get("name", "")}
                    )

                department, _ = Department.objects.update_or_create(
                    id_from_api=dept_data["id"],
                    defaults={
                        "name": dept_data.get("name", ""),
                        "code": dept_data.get("code", ""),
                        "structure_type": struct_type,
                        "locality_type": loc_type,
                        "active": dept_data.get("active", True)
                    }
                )

                # === 5. Semester ===
                sem_data = item.get("semester")
                semester = None
                if sem_data:
                    semester, _ = Semester.objects.update_or_create(
                        code=sem_data.get("code", ""),
                        defaults={"name": sem_data.get("name", "")}
                    )

                # === 6. Curriculum (bog'langan) ===
                curriculum_id = item.get("_curriculum")
                if not curriculum_id:
                    logger.warning(f"O'tkazib yuborildi: _curriculum yo'q, subject id={item.get('id')}")
                    continue
                try:
                    curriculum = Curriculum.objects.get(id_from_api=curriculum_id)
                except Curriculum.DoesNotExist:
                    logger.warning(f"O'tkazib yuborildi: Curriculum topilmadi (id_from_api={curriculum_id})")
                    continue

                # === 7. RatingGrade ===
                rg_data = item.get("ratingGrade")
                rating_grade = None
                if rg_data:
                    rating_grade, _ = RatingGrade.objects.update_or_create(
                        code=rg_data.get("code", ""),
                        defaults={
                            "name": rg_data.get("name", ""),
                            "template": rg_data.get("template", ""),
                            "updated_at": rg_data.get("updated_at", 0)
                        }
                    )

                # === 8. ExamFinish ===
                ef_data = item.get("examFinish")
                exam_finish = None
                if ef_data:
                    exam_finish, _ = ExamFinish.objects.update_or_create(
                        code=ef_data.get("code", ""),
                        defaults={"name": ef_data.get("name", "")}
                    )

                # === 9. Asosiy CurriculumSubject yaratish ===
                cs, created = CurriculumSubject.objects.update_or_create(
                    id_from_api=item["id"],
                    defaults={
                        "subject": subject,
                        "subject_type": subject_type,
                        "subject_block": subject_block,
                        "department": department,
                        "semester": semester,
                        "curriculum": curriculum,
                        "rating_grade": rating_grade,
                        "exam_finish": exam_finish,
                        "total_acload": item.get("total_acload"),
                        "resource_count": item.get("resource_count"),
                        "in_group": item.get("in_group"),
                        "at_semester": item.get("at_semester", True),
                        "active": item.get("active", True),
                        "credit": item.get("credit"),
                        "created_at": item.get("created_at"),
                        "updated_at": item.get("updated_at")
                    }
                )

                # === 10. SubjectDetails (tozalash + qayta yaratish) ===
                cs.details.all().delete()
                subject_details = item.get("subjectDetails") or []
                for detail in subject_details:
                    tt_data = detail.get("trainingType")
                    if not tt_data:
                        continue
                    tt, _ = TrainingType.objects.update_or_create(
                        code=tt_data.get("code", ""),
                        defaults={"name": tt_data.get("name", "")}
                    )
                    SubjectDetail.objects.create(
                        subject=cs,
                        training_type=tt,
                        academic_load=detail.get("academic_load", 0)
                    )

                # === 11. SubjectExamTypes ===
                cs.exam_types.all().delete()
                subject_exam_types = item.get("subjectExamTypes") or []
                for exam in subject_exam_types:
                    et_data = exam.get("examType")
                    if not et_data:
                        continue
                    et, _ = ExamType.objects.update_or_create(
                        code=et_data.get("code", ""),
                        defaults={"name": et_data.get("name", "")}
                    )
                    SubjectExamType.objects.create(
                        subject=cs,
                        exam_type=et,
                        max_ball=exam.get("max_ball", 0)
                    )

            except Exception as e:
                logger.error(f"Fan ma'lumotini qayta ishlashda xatolik (API id={item.get('id')}): {e}")
                continue  # bitta xatolik butun jarayonni to'xtatmasin

        page += 1


def fetch_and_save_curriculum_subject_teachers():
    API_TEACHER_URL = "https://student.zarmeduniver.com/rest/v1/data/curriculum-subject-teacher-list"
    HEADERS = {
        "accept": "application/json",
        "Authorization": "Bearer cC2jZGCaKUpffoWe542NLao7DNkyRka_"
    }

    page = 1
    total_pages = 1

    while page <= total_pages:
        params = {"limit": 200, "page": page}
        try:
            response = requests.get(API_TEACHER_URL, headers=HEADERS, params=params, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"O'qituvchi API so'rovi xatolikka uchradi (sahifa {page}): {e}")
            raise Exception(f"API so'rovi amalga oshmadi: {e}")

        data = response.json()
        items = data.get("data", {}).get("items", [])
        total_pages = data.get("data", {}).get("pagination", {}).get("pageCount", 1)

        for item in items:
            try:
                # === 1. Subject ===
                subj_data = item.get("subject")
                if not subj_data:
                    logger.warning(f"O'tkazib yuborildi: subject yo'q, teacher id={item.get('id')}")
                    continue

                subject, _ = Subject.objects.update_or_create(
                    id_from_api=subj_data["id"],
                    defaults={
                        "name": subj_data.get("name", ""),
                        "code": subj_data.get("code", "")
                    }
                )

                # === 2. Employee ===
                emp_data = item.get("employee")
                if not emp_data:
                    logger.warning(f"O'tkazib yuborildi: employee yo'q, teacher id={item.get('id')}")
                    continue

                employee, _ = Employee.objects.update_or_create(
                    id_from_api=emp_data["id"],
                    defaults={"name": emp_data.get("name", "")}
                )

                # === 3. Group ===
                group_id = item.get("_group")
                if group_id is None:
                    logger.warning(f"O'tkazib yuborildi: _group yo'q, teacher id={item.get('id')}")
                    continue

                group, _ = Group.objects.get_or_create(id_from_api=group_id)

                # === 4. Curriculum ===
                curriculum_id = item.get("_curriculum")
                if curriculum_id is None:
                    logger.warning(f"O'tkazib yuborildi: _curriculum yo'q, teacher id={item.get('id')}")
                    continue

                try:
                    curriculum = Curriculum.objects.get(id_from_api=curriculum_id)
                except Curriculum.DoesNotExist:
                    logger.warning(f"O'tkazib yuborildi: Curriculum topilmadi (id_from_api={curriculum_id})")
                    continue

                # === 5. Semester (kod orqali) ===
                semester_code = item.get("_semester")
                semester = None
                if semester_code:
                    semester, _ = Semester.objects.get_or_create(
                        code=semester_code,
                        defaults={"name": f"{semester_code}-semestr"}
                    )

                # === 6. EducationYear (kod orqali) ===
                ey_code = item.get("_education_year")
                education_year = None
                if ey_code:
                    education_year, _ = EducationYear.objects.get_or_create(
                        code=ey_code,
                        defaults={"name": f"{ey_code}-{int(ey_code) + 1}"}
                    )

                # === 7. Department ===
                dept_id = item.get("_department")
                department = None
                if dept_id is not None:
                    try:
                        department = Department.objects.get(id_from_api=dept_id)
                    except Department.DoesNotExist:
                        logger.warning(f"Department topilmadi (id_from_api={dept_id}), teacher id={item.get('id')}")
                        continue

                # === 8. TrainingType (kod orqali) ===
                tt_code = item.get("_training_type")
                training_type = None
                if tt_code:
                    training_type, _ = TrainingType.objects.get_or_create(
                        code=tt_code,
                        defaults={"name": "Noma'lum ta'lim turi"}
                    )

                # === 9. curriculumSubjectDetail → SubjectDetail ===
                csd_data = item.get("curriculumSubjectDetail")
                subject_detail = None
                if csd_data and "id" in csd_data:
                    try:
                        # Eslatma: SubjectDetail.id — bu Django modelining avtomatik ID si,
                        # lekin API dagi "id" ham xuddi shu ID bo'lishi kerak (agar siz saqlagan bo'lsangiz)
                        subject_detail = SubjectDetail.objects.get(id=csd_data["id"])
                    except SubjectDetail.DoesNotExist:
                        logger.warning(f"SubjectDetail topilmadi (id={csd_data['id']}), teacher id={item.get('id')}")
                        # Agar topilmasa, o'tkazib yuboramiz
                        continue

                # === 10. Asosiy yozuvni saqlash ===
                CurriculumSubjectTeacher.objects.update_or_create(
                    id_from_api=item["id"],
                    defaults={
                        "curriculum": curriculum,
                        "semester": semester,
                        "education_year": education_year,
                        "department": department,
                        "training_type": training_type,
                        "group": group,
                        "subject": subject,
                        "employee": employee,
                        "curriculum_subject_detail": subject_detail,
                        "students_count": item.get("students_count", 0),
                        "active": item.get("active", True),
                        "created_at": item.get("created_at"),
                        "updated_at": item.get("updated_at")
                    }
                )

            except Exception as e:
                logger.error(f"O'qituvchi ma'lumotini qayta ishlashda xatolik (API id={item.get('id')}): {e}")
                continue  # bitta xatolik butun jarayonni to'xtatmasin

        page += 1


def fetch_and_save_employees():
    page = 1
    total_pages = 1

    while page <= total_pages:
        params = {"type": "teacher", "limit": 200, "page": page}
        response = requests.get(API_EMPLOYEE_URL.strip(), headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        items = data.get("data", {}).get("items", [])
        total_pages = data.get("data", {}).get("pagination", {}).get("pageCount", 1)

        for item in items:
            # --- Gender ---
            gender_data = item.get("gender")
            gender = None
            if gender_data and gender_data.get("code"):
                gender, _ = Gender.objects.get_or_create(
                    code=gender_data["code"],
                    defaults={"name": gender_data["name"]}
                )

            # --- Academic Degree (Eslatma: API da "academicDegree", pastki chiziq emas!) ---
            acad_degree_data = item.get("academicDegree")  # ← to'g'ri kalit
            acad_degree = None
            if acad_degree_data and acad_degree_data.get("code"):
                acad_degree, _ = AcademicDegree.objects.get_or_create(
                    code=acad_degree_data["code"],
                    defaults={"name": acad_degree_data["name"]}
                )

            # --- Academic Rank ---
            acad_rank_data = item.get("academicRank")  # ← to'g'ri kalit
            acad_rank = None
            if acad_rank_data and acad_rank_data.get("code"):
                acad_rank, _ = AcademicRank.objects.get_or_create(
                    code=acad_rank_data["code"],
                    defaults={"name": acad_rank_data["name"]}
                )

            # --- Employee yaratish ---
            employee, _ = Employee.objects.update_or_create(
                id_from_api=item["id"],
                defaults={
                    "full_name": item.get("full_name", "").strip(),
                    "short_name": item.get("short_name", "").strip(),
                    "first_name": item.get("first_name", "").strip(),
                    "second_name": item.get("second_name", "").strip(),
                    "third_name": item.get("third_name", "").strip(),
                    "employee_id_number": item.get("employee_id_number", "").strip(),
                    "gender": gender,
                    "birth_date": item.get("birth_date"),
                    "image": item.get("image", "").strip(),
                    "image_full": item.get("image_full", "").strip(),
                    "year_of_enter": item.get("year_of_enter"),
                    "specialty": item.get("specialty", "").strip(),
                    "academic_degree": acad_degree,
                    "academic_rank": acad_rank,
                    "active": item.get("active", True),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                }
            )

            # --- Staff Position (Muhim: API da "staffPosition") ---
            staff_pos_data = item.get("staffPosition")  # ← to'g'ri kalit!
            staff_pos = None
            if staff_pos_data and staff_pos_data.get("code"):
                staff_pos, _ = StaffPosition.objects.get_or_create(
                    code=staff_pos_data["code"],
                    defaults={"name": staff_pos_data["name"]}
                )

            # --- Employment Form ---
            emp_form_data = item.get("employmentForm")
            emp_form = None
            if emp_form_data and emp_form_data.get("code"):
                emp_form, _ = EmploymentForm.objects.get_or_create(
                    code=emp_form_data["code"],
                    defaults={"name": emp_form_data["name"]}
                )

            # --- Employment Staff ---
            emp_staff_data = item.get("employmentStaff")
            emp_staff = None
            if emp_staff_data and emp_staff_data.get("code"):
                emp_staff, _ = EmploymentStaff.objects.get_or_create(
                    code=emp_staff_data["code"],
                    defaults={"name": emp_staff_data["name"]}
                )

            # --- Employee Status ---
            emp_status_data = item.get("employeeStatus")
            emp_status = None
            if emp_status_data and emp_status_data.get("code"):
                emp_status, _ = EmployeeStatus.objects.get_or_create(
                    code=emp_status_data["code"],
                    defaults={"name": emp_status_data["name"]}
                )

            # --- Employee Type ---
            emp_type_data = item.get("employeeType")
            emp_type = None
            if emp_type_data and emp_type_data.get("code"):
                emp_type, _ = EmployeeType.objects.get_or_create(
                    code=emp_type_data["code"],
                    defaults={"name": emp_type_data["name"]}
                )

            # --- Department (tuzilishini ham to'g'rilab olish kerak) ---
            dept_data = item.get("department")
            department = None
            if dept_data and dept_data.get("id"):
                # StructureType va LocalityType ni ham yaratish/yoki topish
                struct_type_data = dept_data.get("structureType")
                struct_type = None
                if struct_type_data and struct_type_data.get("code"):
                    struct_type, _ = StructureType.objects.get_or_create(
                        code=struct_type_data["code"],
                        defaults={"name": struct_type_data["name"]}
                    )

                locality_type_data = dept_data.get("localityType")
                locality_type = None
                if locality_type_data and locality_type_data.get("code"):
                    locality_type, _ = LocalityType.objects.get_or_create(
                        code=locality_type_data["code"],
                        defaults={"name": locality_type_data["name"]}
                    )

                department, _ = Department.objects.update_or_create(
                    id_from_api=dept_data["id"],
                    defaults={
                        "name": dept_data.get("name", ""),
                        "code": dept_data.get("code", ""),
                        "structure_type": struct_type,
                        "locality_type": locality_type,
                        "active": dept_data.get("active", True),
                    }
                )

            # --- EmployeeAssignment ---
            EmployeeAssignment.objects.update_or_create(
                employee=employee,
                meta_id=item["meta_id"],
                defaults={
                    "department": department,
                    "staff_position": staff_pos,
                    "employment_form": emp_form,
                    "employment_staff": emp_staff,
                    "employee_status": emp_status,
                    "employee_type": emp_type,
                    "contract_number": item.get("contract_number", "").strip(),
                    "decree_number": item.get("decree_number", "").strip(),
                    "contract_date": item.get("contract_date"),
                    "decree_date": item.get("decree_date"),
                    "active": item.get("active", True),
                    "hash": item.get("hash", "").strip(),
                }
            )

        page += 1


def fetch_and_save_groups():
    page = 1
    total_pages = 1

    while page <= total_pages:
        params = {"limit": 200, "page": page}
        try:
            response = requests.get(API_GROUP_URL, headers=HEADERS, params=params, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Guruhlar API xatolik (sahifa {page}): {e}")
            raise Exception(f"API so'rovi amalga oshmadi: {e}")

        data = response.json()
        items = data.get("data", {}).get("items", [])
        total_pages = data.get("data", {}).get("pagination", {}).get("pageCount", 1)

        for item in items:
            try:
                Group.objects.update_or_create(
                    id_from_api=item["id"],
                    defaults={
                        "name": item.get("name", "").strip() or f"Guruh {item['id']}"
                    }
                )
            except Exception as e:
                logger.error(f"Guruh ma'lumotini saqlashda xatolik (id={item.get('id')}): {e}")
                continue

        page += 1

def fetch_and_save_students():
    page = 1
    total_pages = 1

    while page <= total_pages:
        params = {"limit": 200, "page": page}
        response = requests.get(API_STUDENT_URL.strip(), headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        items = data.get("data", {}).get("items", [])
        total_pages = data.get("data", {}).get("pagination", {}).get("pageCount", 1)

        for item in items:
            # --- Gender ---
            gender = None
            gender_data = item.get("gender")
            if gender_data and gender_data.get("code"):
                gender, _ = Gender.objects.get_or_create(
                    code=gender_data["code"],
                    defaults={"name": gender_data["name"]}
                )

            # --- StudentStatus ---
            status = None
            status_data = item.get("studentStatus")
            if status_data and status_data.get("code"):
                status, _ = StudentStatus.objects.get_or_create(
                    code=status_data["code"],
                    defaults={"name": status_data["name"]}
                )

            # --- EducationForm ---
            edu_form = None
            edu_form_data = item.get("educationForm")
            if edu_form_data and edu_form_data.get("code"):
                edu_form, _ = EducationForm.objects.get_or_create(
                    code=edu_form_data["code"],
                    defaults={"name": edu_form_data["name"]}
                )

            # --- EducationType ---
            edu_type = None
            edu_type_data = item.get("educationType")
            if edu_type_data and edu_type_data.get("code"):
                edu_type, _ = EducationType.objects.get_or_create(
                    code=edu_type_data["code"],
                    defaults={"name": edu_type_data["name"]}
                )

            # --- Specialty ---
            specialty = None
            spec_data = item.get("specialty")
            if spec_data and spec_data.get("id"):
                specialty, _ = Specialty.objects.get_or_create(
                    id_from_api=spec_data["id"],
                    defaults={
                        "code": spec_data.get("code", ""),
                        "name": spec_data.get("name", ""),
                    }
                )

            # --- Group ---
            group = None
            group_data = item.get("group")
            if group_data and group_data.get("id"):
                group, _ = Group.objects.get_or_create(
                    id_from_api=group_data["id"],
                    defaults={"name": group_data.get("name", "").strip()}
                )

            # --- Department ---
            dept = None
            dept_data = item.get("department")
            if dept_data and dept_data.get("id"):
                dept, _ = Department.objects.get_or_create(
                    id_from_api=dept_data["id"],
                    defaults={
                        "name": dept_data.get("name", ""),
                        "code": dept_data.get("code", ""),
                        # structure_type va locality_type ham kerak bo'lsa, qo'shish kerak
                    }
                )

            # --- Student yaratish ---
            Student.objects.update_or_create(
                id_from_api=item["id"],
                defaults={
                    "student_id_number": item.get("student_id_number", "").strip(),
                    "full_name": item.get("full_name", "").strip(),
                    "short_name": item.get("short_name", "").strip(),
                    "first_name": item.get("first_name", "").strip(),
                    "second_name": item.get("second_name", "").strip(),
                    "third_name": item.get("third_name", "").strip(),
                    "gender": gender,
                    "birth_date": item.get("birth_date"),
                    "image_full": item.get("image", "").strip(),
                    "avg_gpa": item.get("avg_gpa", 0.0),
                    "avg_grade": item.get("avg_grade", 0.0),
                    "student_status": status,
                    "education_form": edu_form,
                    "education_type": edu_type,
                    "specialty": specialty,
                    "group": group,
                    "department": dept,
                    "level": item.get("level", {}).get("name", "") if item.get("level") else "",
                    "semester": item.get("semester", {}).get("name", "") if item.get("semester") else "",
                    "year_of_enter": item.get("year_of_enter"),
                    "active": True,
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                }
            )

        page += 1