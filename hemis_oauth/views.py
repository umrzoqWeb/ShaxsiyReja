# hemis_oauth/views.py
import secrets
from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest
from django.contrib.auth import get_user_model, login
from django.views.decorators.http import require_GET
from .client import HemisOAuthClient
from django.contrib.auth import login, authenticate, logout
import requests
from .models import CustomUser

User = get_user_model()


def _session_set(request, key, value):
    request.session[key] = value
    request.session.modified = True


def _session_pop(request, key, default=None):
    val = request.session.get(key, default)
    if key in request.session:
        del request.session[key]
    return val


def _nice(s: str | None) -> str:
    """
    Yozuvni saranjom qilish: strip + title.
    Agar original registrni saqlamoqchi bo'lsangiz, .title()ni olib tashlang.
    """
    s = (s or "").strip()
    return s.title() if s else s

def _to_upper(s: str | None) -> str:
    s = (s or "").strip()
    return s.upper()


def _apply_basic_profile_fields(user: User, userinfo: dict) -> None:
    """
    user.first_name / user.last_name va email ni userinfo asosida to'ldiradi.
    """





    first = _to_upper(userinfo.get("firstname"))
    last  = _to_upper(userinfo.get("surname"))

    # Agar firstname/surname bo'sh bo'lsa, 'name'ni bo'lib olishga urinamiz.
    if not first or not last:
        full = (userinfo.get("name") or "").strip()
        parts = [p for p in full.split() if p]
        if not first and parts:
            first = _to_upper(parts[0])
        if not last and len(parts) > 1:
            last = _to_upper(parts[-1])

    email = (userinfo.get("email") or "").strip()

    update_fields = []

    if first and user.first_name != first:
        user.first_name = first
        update_fields.append("first_name")

    if last and user.last_name != last:
        user.last_name = last
        update_fields.append("last_name")

    # E-mail kelgan va foydalanuvchida yo'q/bo'sh bo'lsa, yozib qo'yamiz
    if email and (not user.email):
        user.email = email
        update_fields.append("email")

    if update_fields:
        user.save(update_fields=update_fields)


@require_GET
def select_login(request):
    return render(request, "hemis_oauth/select.html")


@require_GET
def login_start(request, profile: str):
    profile = profile.lower()
    if profile not in {"employee", "student"}:
        return HttpResponseBadRequest("Noto‘g‘ri profil")
    # profile = 'employee'
    state = secrets.token_urlsafe(24)
    _session_set(request, "hemis_oauth_state", state)
    _session_set(request, "hemis_oauth_profile", profile)

    client = HemisOAuthClient(profile=profile)
    return redirect(client.build_authorize_url(state))


@require_GET
def callback(request):
    err = request.GET.get("error")
    if err:
        return HttpResponseBadRequest(f"OAuth error: {err}")

    code = request.GET.get("code")
    state = request.GET.get("state")
    state_saved = _session_pop(request, "hemis_oauth_state")
    profile_type = _session_pop(request, "hemis_oauth_profile")  # 'employee' yoki 'student'

    if not code or not state or state != state_saved or not profile_type:
        return HttpResponseBadRequest("Invalid OAuth state yoki profile topilmadi")

    client = HemisOAuthClient(profile=profile_type)

    # 1) Code → Token
    token_data = client.fetch_token(code)
    access_token = token_data.get("access_token")
    if not access_token:
        return HttpResponseBadRequest("Access token olinmadi")

    # 2) Token → Userinfo
    userinfo = client.fetch_userinfo(access_token)
    # print(userinfo)

    hemis_uuid = str(userinfo.get("uuid") or userinfo.get("id") or "")
    username = (userinfo.get("login") or hemis_uuid or f"hemis_{profile_type}_{secrets.token_hex(4)}").strip()
    email = (userinfo.get("email") or "").strip()

    # 3) IDni aniqlash
    if profile_type == 'employee':
        id_value = userinfo.get("employee_id_number")
        if not id_value:
            return HttpResponseBadRequest("Xodim ID (employee_id_number) HEMISdan olinmadi")
        lookup = {'employee_id': id_value}
        defaults = {'user_type': 'employee', 'email': email}
    else:  # student
        id_value = userinfo.get("student_id_number")  # HEMIS talaba IDsi
        if not id_value:
            return HttpResponseBadRequest("Talaba ID (student_id_number) HEMISdan olinmadi")
        lookup = {'student_id': str(id_value)}
        defaults = {'user_type': 'student', 'email': email}

    # 4) Foydalanuvchini yaratish/yoki topish
    try:
        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={**lookup, **defaults}
        )
        if created:
            # Yangi foydalanuvchi yaratildi
            pass
        else:
            # Mavjud foydalanuvchi — agar ID bo'sh bo'lsa, to'ldirish
            if profile_type == 'employee' and not user.employee_id:
                user.employee_id = lookup['employee_id']
                user.user_type = 'employee'
                user.save()
            elif profile_type == 'student' and not user.student_id:
                user.student_id = lookup['student_id']
                user.user_type = 'student'
                user.save()
    except IntegrityError:
        # ID konfliktsi — boshqa username bilan urinish
        username = f"{username}_{secrets.token_hex(4)}"
        user = CustomUser.objects.create(username=username, **lookup, **defaults)

    # 5) Profil ma'lumotlarini yangilash
    _apply_basic_profile_fields(user, userinfo)

    # 6) Tizimga kiritish
    login(request, user)
    return redirect("/")


def logout_view(request):
    logout(request)
    # requests.get("https://hemis.zarmeduniver.com/dashboard/login", timeout=5)
    return redirect("/")