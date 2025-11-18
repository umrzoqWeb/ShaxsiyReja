from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.contrib import messages

from hemis_integratsiya.models import Employee, EmployeeAssignment, CurriculumSubjectTeacher, Student
from .models import EmployeeActivity, ActivityReview, StudentActivity, Reviewer
from .utils import MEZON_CATEGORIES, get_reviewers_for_activity, get_section_for_activity_type, STUDENT_MEZON_CATEGORIES
from django.contrib.auth import get_user_model
from .forms import StudentActivityForm
User = get_user_model()

# --- Home va yuklama ---
@login_required
def home_view(request):
    if request.user.user_type == 'employee':

        employee = None
        assignments = None

        if request.user.is_authenticated and hasattr(request.user, 'employee_id'):
            try:
                employee = Employee.objects.get(employee_id_number=request.user.employee_id)
                assignments = employee.assignments.filter(active=True).select_related(
                    'department',
                    'staff_position',
                    'employment_form',
                    'employment_staff',
                    'employee_status',
                    'employee_type'
                )
            except Employee.DoesNotExist:
                employee = None

        return render(request, 'main/home_employee.html', {
            'employee': employee,
            'assignments': assignments,
        })

    elif request.user.user_type == 'student':
        # Talaba uchun yangi kod
        student = None
        if hasattr(request.user, 'student_id') and request.user.student_id:
            try:
                student = Student.objects.get(student_id_number=request.user.student_id)
            except Student.DoesNotExist:
                pass
        # student.image_full = student.image_full.replace('uploads/', '')
        return render(request, 'main/home_student.html', {'student': student})
    print(request.user.user_type)
    return redirect('select')


@login_required
def yuklama_view(request):
    employee_id = getattr(request.user, 'employee_id', None)
    if not employee_id:
        yuklama = []
    else:
        yuklama = CurriculumSubjectTeacher.objects.select_related(
            'subject', 'curriculum', 'semester', 'group'
        ).filter(
            employee__employee_id_number=employee_id
        ).order_by('semester__code', 'subject__name')

    return render(request, 'main/yuklama.html', {'yuklama': yuklama})


# --- Kategoriyani aniqlash (yangi mantiq) ---
def get_employee_and_category(request):
    if not hasattr(request.user, 'employee_id'):
        return None, None, None
    try:
        emp = Employee.objects.get(employee_id_number=request.user.employee_id)
        cat = emp.get_category()  # Employee modelidagi usul
        return emp, None, cat
    except Employee.DoesNotExist:
        return None, None, None


# --- Me’yonlar ro‘yxatlari ---
def taught_view(request):
    emp, _, cat = get_employee_and_category(request)
    if not emp or not cat:
        return render(request, 'main/error.html', {'msg': 'Xodim topilmadi'})

    mezonlar = MEZON_CATEGORIES[cat]['taught']
    mezon_data = []
    for code, name, max_ball in mezonlar:
        count = EmployeeActivity.objects.filter(employee=emp, activity_type=code).count()
        latest = EmployeeActivity.objects.filter(employee=emp, activity_type=code).order_by('-created_at').first()
        mezon_data.append({
            'code': code,
            'name': name,
            'max_ball': max_ball,
            'count': count,
            'latest_status': latest.get_status_display() if latest else None,
            'latest': latest
        })

    return render(request, 'main/mezon_list.html', {
        'section_title': 'Oʼquv-uslubiy ishlar va taʼlim sifati',
        'mezon_data': mezon_data,
        'employee': emp,
        'category': cat,
    })


def research_view(request):
    emp, _, cat = get_employee_and_category(request)
    if not emp or not cat:
        return render(request, 'main/error.html', {'msg': 'Xodim topilmadi'})

    mezonlar = MEZON_CATEGORIES[cat]['research']
    mezon_data = []
    for code, name, max_ball in mezonlar:
        count = EmployeeActivity.objects.filter(employee=emp, activity_type=code).count()
        latest = EmployeeActivity.objects.filter(employee=emp, activity_type=code).order_by('-created_at').first()
        mezon_data.append({
            'code': code,
            'name': name,
            'max_ball': max_ball,
            'count': count,
            'latest_status': latest.get_status_display() if latest else None,
            'latest': latest
        })

    return render(request, 'main/mezon_list.html', {
        'section_title': 'Ilmiy-innovatsion faoliyat',
        'mezon_data': mezon_data,
        'employee': emp,
        'category': cat,
    })


def social_view(request):
    emp, _, cat = get_employee_and_category(request)
    if not emp or not cat:
        return render(request, 'main/error.html', {'msg': 'Xodim topilmadi'})

    mezonlar = MEZON_CATEGORIES[cat]['social']
    mezon_data = []
    for code, name, max_ball in mezonlar:
        count = EmployeeActivity.objects.filter(employee=emp, activity_type=code).count()
        latest = EmployeeActivity.objects.filter(employee=emp, activity_type=code).order_by('-created_at').first()
        mezon_data.append({
            'code': code,
            'name': name,
            'max_ball': max_ball,
            'count': count,
            'latest_status': latest.get_status_display() if latest else None,
            'latest': latest
        })

    return render(request, 'main/mezon_list.html', {
        'section_title': 'Ijtimoiy-maʼnaviy faoliyat, ijro intizomi',
        'mezon_data': mezon_data,
        'employee': emp,
        'category': cat,
    })


# --- Bitta me’zon bo‘yicha ishlar ---
def mezon_detail_view(request, activity_type):
    emp, _, cat = get_employee_and_category(request)
    if not emp or not cat:
        return redirect('home')

    allowed_codes = []
    for group in MEZON_CATEGORIES[cat].values():
        allowed_codes.extend([code for code, _, _ in group])
    if activity_type not in allowed_codes:
        return redirect('home')

    mezon_name = None
    max_ball = 0
    for group in MEZON_CATEGORIES[cat].values():
        for code, name, ball in group:
            if code == activity_type:
                mezon_name = name
                max_ball = ball
                break
        if mezon_name:
            break

    activities = EmployeeActivity.objects.filter(
        employee=emp, activity_type=activity_type
    ).order_by('-created_at')

    return render(request, 'main/mezon_detail.html', {
        'mezon_name': mezon_name,
        'activity_type': activity_type,
        'activities': activities,
        'max_ball': max_ball,
    })


# --- Yangi ish yuklash (tuzatilgan) ---
class ActivityForm(forms.ModelForm):
    class Meta:
        model = EmployeeActivity
        fields = ['title', 'description', 'evidence_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hujjat nomini kiriting'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Qo‘shimcha izoh...'}),
            'evidence_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Hujjat nomi',
            'description': 'Izoh',
            'evidence_file': 'Faylni yuklang',
        }


def add_activity_view(request, activity_type):
    emp, _, cat = get_employee_and_category(request)
    if not emp or not cat:
        return redirect('home')

    # Tayinlovni tanlash: avval employment_form=11, keyin eng yuqori staff_position
    assignments = emp.assignments.filter(active=True)
    assignment = None
    for a in assignments:
        if a.employment_form and a.employment_form.code == "11":
            assignment = a
            break
    if assignment is None and assignments.exists():
        valid = [a for a in assignments if a.staff_position and a.staff_position.code.isdigit()]
        if valid:
            assignment = max(valid, key=lambda x: int(x.staff_position.code))
    if not assignment:
        return redirect('home')

    # Mezon nomini topish
    mezon_name = "Noma'lum"
    for group in MEZON_CATEGORIES[cat].values():
        for code, name, _ in group:
            if code == activity_type:
                mezon_name = name
                break
        if mezon_name != "Noma'lum":
            break

    if request.method == "POST":
        form = ActivityForm(request.POST, request.FILES)
        if form.is_valid():
            act = form.save(commit=False)
            act.employee = emp
            act.assignment = assignment  # ✅ Endi to'g'ri tayinlov
            act.activity_type = activity_type
            act.status = 'pending'
            act.save()
            return redirect('mezon_detail', activity_type=activity_type)
    else:
        form = ActivityForm()

    return render(request, 'main/add_activity.html', {
        'form': form,
        'mezon_name': mezon_name,
        'activity_type': activity_type,
    })

def _build_mezon_data(employee, mezonlar):
    from .models import EmployeeActivity
    data = []
    for code, name, max_ball in mezonlar:
        count = EmployeeActivity.objects.filter(employee=employee, activity_type=code).count()
        latest = EmployeeActivity.objects.filter(employee=employee, activity_type=code).order_by('-created_at').first()
        data.append({
            'code': code,
            'name': name,
            'max_ball': max_ball,
            'count': count,
            'latest_status': latest.get_status_display() if latest else None,
            'latest': latest
        })
    return data

# --- Tekshiruvchilar uchun ---

@login_required
def reviewer_dashboard(request):
    try:
        request.user.reviewer
    except Reviewer.DoesNotExist:
        return render(request, 'main/error.html', {'msg': 'Siz tekshiruvchi emassiz.'})

    all_activities = EmployeeActivity.objects.all()
    print(f"Barcha ishlar soni: {all_activities.count()}")

    allowed_types = []
    for cat in [1, 2, 3]:
        for sec in ['taught', 'research', 'social']:
            for code, _, _ in MEZON_CATEGORIES[cat][sec]:
                allowed_types.append(code)

    print(f"Ruxsat etilgan mezonlar: {allowed_types}")

    activities = EmployeeActivity.objects.filter(
        activity_type__in=allowed_types,
        status='pending'
    )

    print(f"Ko'rinadigan ishlar: {activities.count()}")
    for act in activities:
        print(f"- {act.employee.full_name}: {act.get_activity_type_display()}, Status: {act.status}")

    my_activities = []

    for act in activities:
        reviewers = get_reviewers_for_activity(act)
        if request.user in reviewers:
            already_reviewed = act.reviews.filter(reviewer=request.user).exists()
            my_activities.append({
                'activity': act,
                'already_reviewed': already_reviewed
            })

    print(f"Siz uchun ishlar: {len(my_activities)} ta")

    return render(request, 'main/reviewer_dashboard.html', {
        'my_activities': my_activities,
    })

@login_required
def review_activity(request, activity_id):
    try:
        reviewer = request.user.reviewer
    except Reviewer.DoesNotExist:
        return redirect('home')

    activity = get_object_or_404(EmployeeActivity, id=activity_id, status='pending')

    # Tekshiruvchining ushbu mezon turini ko'rish huquqi bormi?
    allowed = False
    for cat in [1, 2, 3]:
        for sec in ['taught', 'research', 'social']:
            if getattr(reviewer, f'can_review_employee_{sec}', False):  # ✅ Yangi nom
                codes = [code for code, _, _ in MEZON_CATEGORIES[cat][sec]]
                if activity.activity_type in codes:
                    allowed = True
                    break
        if allowed:
            break

    if not allowed:
        return redirect('reviewer_dashboard')

    if request.method == "POST":
        action = request.POST.get('action')
        comment = request.POST.get('comment', '').strip()
        points = float(request.POST.get('points') or 0)

        if action == 'approve':
            ActivityReview.objects.create(
                activity=activity,
                reviewer=request.user,
                decision='approve',
                points=points
            )
        elif action == 'reject':
            if not comment:
                return render(request, 'main/review_activity.html', {
                    'activity': activity,
                    'error': 'Rad etish uchun izoh kiritish shart.'
                })
            ActivityReview.objects.create(
                activity=activity,
                reviewer=request.user,
                decision='reject',
                comment=comment
            )

        # Holatni yangilash
        update_activity_status(activity)
        return redirect('reviewer_dashboard')

    return render(request, 'main/review_activity.html', {'activity': activity})

def update_activity_status(activity):
    reviewers = get_reviewers_for_activity(activity)
    reviews = activity.reviews.all()

    if reviews.count() < reviewers.count():
        return

    if reviews.filter(decision='reject').exists():
        activity.status = 'rejected'
        activity.final_points = 0
    else:
        total = sum(r.points for r in reviews)
        avg = total / reviews.count() if reviews.count() > 0 else 0
        activity.status = 'approved'
        activity.final_points = round(avg, 2)

    activity.save()



@login_required
def student_taught_view(request):
    return _student_section_view(request, 'taught', 'Ta’lim faoliyati')

@login_required
def student_research_view(request):
    return _student_section_view(request, 'research', 'Ilmiy-innovatsion faoliyat')

@login_required
def student_social_view(request):
    return _student_section_view(request, 'social', 'Ijtimoiy, ma’naviy-ma’rifiy faollik')

def _student_section_view(request, section, title):
    if request.user.user_type != 'student':
        return redirect('home')
    try:
        student = Student.objects.get(student_id_number=request.user.student_id)
    except Student.DoesNotExist:
        return render(request, 'main/error.html', {'msg': 'Talaba topilmadi'})

    mezonlar = STUDENT_MEZON_CATEGORIES[section]
    mezon_data = []
    for code, name, max_ball, needs_doc in mezonlar:
        count = StudentActivity.objects.filter(student=student, activity_type=code).count()
        latest = StudentActivity.objects.filter(student=student, activity_type=code).order_by('-created_at').first()
        mezon_data.append({
            'code': code,
            'name': name,
            'max_ball': max_ball,
            'needs_document': needs_doc,
            'count': count,
            'latest': latest
        })

    return render(request, 'main/student_mezon_list.html', {
        'section_title': title,
        'mezon_data': mezon_data,
        'section': section,
    })

def _build_student_mezon_data(student, mezonlar):
    from .models import StudentActivity
    data = []
    for code, name, max_ball, needs_doc in mezonlar:
        count = StudentActivity.objects.filter(student=student, activity_type=code).count()
        latest = StudentActivity.objects.filter(student=student, activity_type=code).order_by('-created_at').first()
        data.append({
            'code': code,
            'name': name,
            'max_ball': max_ball,
            'needs_document': needs_doc,
            'count': count,
            'latest': latest
        })
    return data

def student_add_activity_view(request, section, activity_type):
    if request.user.user_type != 'student':
        return redirect('home')
    try:
        student = Student.objects.get(student_id_number=request.user.student_id)
    except Student.DoesNotExist:
        return redirect('home')

    # Mezon haqida ma'lumot
    mezon_info = None
    for code, name, max_ball, needs_doc in STUDENT_MEZON_CATEGORIES[section]:
        if code == activity_type:
            mezon_info = {'name': name, 'needs_doc': needs_doc, 'max_ball': max_ball}
            break
    if not mezon_info or not mezon_info['needs_doc']:
        return redirect('home')  # Faqat hujjat talab qilinadigan mezonlar

    if request.method == "POST":
        form = StudentActivityForm(request.POST, request.FILES)
        if form.is_valid():
            act = form.save(commit=False)
            act.student = student
            act.activity_type = activity_type
            act.section = section
            act.save()
            return redirect('student_mezon_detail', section=section, activity_type=activity_type)
    else:
        form = StudentActivityForm()

    return render(request, 'main/student_add_activity.html', {
        'form': form,
        'mezon_name': mezon_info['name'],
        'activity_type': activity_type,
        'section': section,
    })


@login_required
def student_mezon_detail_view(request, section, activity_type):
    if request.user.user_type != 'student':
        return redirect('home')

    try:
        student = Student.objects.get(student_id_number=request.user.student_id)
    except Student.DoesNotExist:
        return render(request, 'main/error.html', {'msg': 'Talaba topilmadi'})

    # Mezon haqida ma'lumot
    mezon_info = None
    for code, name, max_ball, needs_doc in STUDENT_MEZON_CATEGORIES[section]:
        if code == activity_type:
            mezon_info = {'name': name, 'max_ball': max_ball, 'needs_document': needs_doc}
            break

    if not mezon_info:
        return redirect('home')

    # Ushbu mezon bo'yicha barcha ishlarni olish
    activities = StudentActivity.objects.filter(
        student=student,
        activity_type=activity_type
    ).order_by('-created_at')

    return render(request, 'main/student_mezon_detail.html', {
        'mezon_name': mezon_info['name'],
        'section': section,
        'activity_type': activity_type,
        'activities': activities,
        'max_ball': mezon_info['max_ball'],
        'needs_document': mezon_info['needs_document'],
    })


@login_required
def help_student(request):
    return render(request, 'main/help_student.html')

@login_required
def help_teacher(request):
    return render(request, 'main/help_teacher.html')

@login_required
def student_reviewer_dashboard(request):
    try:
        reviewer = request.user.reviewer
    except Reviewer.DoesNotExist:
        return render(request, 'main/error.html', {'msg': 'Siz talaba ishlarini tekshiruvchisi emassiz.'})

    # Qaysi bo'limlarni ko'radi?
    sections = []
    if reviewer.can_review_student_taught:      # ✅ Yangi nom
        sections.append('taught')
    if reviewer.can_review_student_research:    # ✅ Yangi nom
        sections.append('research')
    if reviewer.can_review_student_social:      # ✅ Yangi nom
        sections.append('social')

    if not sections:
        return render(request, 'main/error.html', {'msg': 'Siz hech qanday bo\'limni tekshirmaysiz.'})

    # Faqat "jarayonda" bo'lgan talaba ishlarini olish
    activities = StudentActivity.objects.filter(
        section__in=sections,
        status='pending'
    ).select_related('student')

    return render(request, 'main/student_reviewer_dashboard.html', {
        'activities': activities,
        'sections': sections,
    })

@login_required
def review_student_activity(request, activity_id):
    try:
        reviewer = request.user.reviewer
    except Reviewer.DoesNotExist:
        return redirect('home')

    activity = get_object_or_404(StudentActivity, id=activity_id, status='pending')

    # Tekshiruvchining ushbu bo'limni ko'rish huquqi bormi?
    # ✅ Yangi nomlarga o'tildi
    if (activity.section == 'taught' and not reviewer.can_review_student_taught) or \
       (activity.section == 'research' and not reviewer.can_review_student_research) or \
       (activity.section == 'social' and not reviewer.can_review_student_social):
        return redirect('student_reviewer_dashboard')

    if request.method == "POST":
        action = request.POST.get('action')
        comment = request.POST.get('comment', '').strip()
        points = float(request.POST.get('points') or 0)

        if action == 'approve':
            StudentReview.objects.create(
                activity=activity,
                reviewer=request.user,
                decision='approve',
                points=points
            )
        elif action == 'reject':
            if not comment:
                return render(request, 'main/review_student_activity.html', {
                    'activity': activity,
                    'error': 'Rad etish uchun izoh kiritish shart.'
                })
            StudentReview.objects.create(
                activity=activity,
                reviewer=request.user,
                decision='reject',
                comment=comment,
                points=0
            )

        # Holatni yangilash — talabalar uchun oddiy: bitta tekshiruvchi yetarli
        reviews = activity.reviews.all()
        if reviews.exists():
            last_review = reviews.latest('reviewed_at')
            activity.status = 'approved' if last_review.decision == 'approve' else 'rejected'
            activity.final_points = last_review.points if last_review.decision == 'approve' else 0
            activity.save()

        return redirect('student_reviewer_dashboard')

    return render(request, 'main/review_student_activity.html', {
        'activity': activity,
        'max_ball': get_max_ball_for_student_activity(activity.activity_type),
    })

def get_max_ball_for_student_activity(activity_type):
    from .utils import STUDENT_MEZON_CATEGORIES
    for section in STUDENT_MEZON_CATEGORIES.values():
        for code, name, max_ball, _ in section:
            if code == activity_type:
                return max_ball
    return 0

@login_required
def assign_points_to_student_activity(request, activity_id):
    # Foydalanuvchi tekshiruvchimi?
    try:
        reviewer = request.user.reviewer
    except:
        messages.error(request, "Siz tekshiruvchi emassiz.")
        return redirect('home')

    activity = get_object_or_404(StudentActivity, id=activity_id)

    # Tekshiruvchi ushbu mezonni tekshirish huquqiga ega emasmikin?
    section_field = f'can_review_student_{activity.section}'
    if not getattr(reviewer, section_field, False):
        messages.error(request, "Siz ushbu mezonni tekshirish huquqiga ega emassiz.")
        return redirect('student_reviewer_dashboard')

    # Hujjat talab qilinmasa — ball qo'yish mumkin
    if activity.requires_document():
        messages.error(request, "Bu mezon hujjat talab qiladi. Uni bu sahifada baholab bo'lmaydi.")
        return redirect('student_reviewer_dashboard')

    if request.method == "POST":
        points = float(request.POST.get('points', 0))
        comment = request.POST.get('comment', '').strip()

        # Maksimal ballni tekshirish
        max_ball = get_max_ball_for_student_activity(activity.activity_type)
        if points > max_ball:
            messages.error(request, f"Ball maksimal ({max_ball}) qiymatdan oshib ketmasin.")
        else:
            activity.final_points = points
            activity.status = 'approved'
            activity.save()

            messages.success(request, f"Ball muvaffaqiyatli qo'yildi: {points}")
            return redirect('student_reviewer_dashboard')

    max_ball = get_max_ball_for_student_activity(activity.activity_type)

    return render(request, 'main/assign_points.html', {
        'activity': activity,
        'max_ball': max_ball,
    })

