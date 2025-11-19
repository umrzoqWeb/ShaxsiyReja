# main/utils.py
from django.contrib.auth import get_user_model
User = get_user_model()

MEZON_CATEGORIES = {
    1: {
        'taught': [
            ('textbook', 'Darslik', 30),
            ('manual', 'O‘quv/kl. qo‘llanma', 20),
            ('mobility', 'Akademik mobilnost', 20),
            ('method_guide', 'O‘quv-uslubiy tavsiyanoma', 10),
            ('teaching_quality', 'Ta’lim sifati', 20),
        ],
        'research': [
            ('patent', 'Ixtiroga patent', 15),
            ('project', 'Xalqaro/Respublika loyihasi', 15),
            ('phd_supervision', 'PhD/DSc rahbarlik', 10),
            ('diss_defense', 'Dissertatsiya himoyasi', 15),
            ('monograph', 'Monografiya', 5),
            ('scopus', 'Scopus maqola', 15),
            ('wos', 'Web of Science', 10),
            ('oak', 'OAK jurnal', 5),
            ('olympiad_mentor', 'Olimpiada/tanlov rahbari', 10),
        ],
        'social': [
            ('creative_circle', 'Ijodiy/sport to‘garak', 40),
            ('media', 'OAVda ishtirok', 30),
            ('personal_plan', 'Shaxsiy ish rejasi', 15),
            ('discipline', 'Ijro intizomi', 15),
        ]
    },
    2: {
        'taught': [
            ('manual', 'O‘quv/kl. qo‘llanma', 50),
            ('method_guide', 'O‘quv-uslubiy tavsiyanoma', 20),
            ('teaching_quality', 'Ta’lim sifati', 30),
        ],
        'research': [
            ('diss_defense', 'PhD/DSc himoyasi', 30),
            ('monograph', 'Monografiya', 10),
            ('scopus', 'Scopus maqola', 20),
            ('wos', 'Web of Science', 15),
            ('oak', 'OAK jurnal', 10),
            ('olympiad_mentor', 'Olimpiada/tanlov rahbari', 15),
        ],
        'social': [
            ('creative_circle', 'Ijodiy/sport to‘garak', 40),
            ('media', 'OAVda ishtirok', 30),
            ('personal_plan', 'Shaxsiy ish rejasi', 15),
            ('discipline', 'Ijro intizomi', 15),
        ]
    },
    3: {
        'taught': [
            ('manual', 'O‘quv qo‘llanma', 40),
            ('method_guide', 'O‘quv-uslubiy tavsiyanoma', 30),
            ('teaching_quality', 'Ta’lim sifati', 30),
        ],
        'research': [
            ('phd_topic_approval', 'PhD mavzusini tasdiqlash', 15),
            ('diss_defense', 'PhD dissertatsiya himoyasi', 30),
            ('scopus', 'Scopus maqola', 20),
            ('wos', 'Web of Science', 10),
            ('oak', 'OAK jurnal', 10),
            ('olympiad_mentor', 'Olimpiada/tanlov rahbari', 10),
        ],
        'social': [
            ('creative_circle', 'Ijodiy/sport to‘garak', 40),
            ('media', 'OAVda ishtirok', 30),
            ('personal_plan', 'Shaxsiy ish rejasi', 15),
            ('discipline', 'Ijro intizomi', 15),
        ]
    }
}

def get_section_for_activity_type(activity_type):
    for cat in [1, 2, 3]:
        if activity_type in [code for code, _, _ in MEZON_CATEGORIES[cat]['taught']]:
            return 'taught'
        if activity_type in [code for code, _, _ in MEZON_CATEGORIES[cat]['research']]:
            return 'research'
        if activity_type in [code for code, _, _ in MEZON_CATEGORIES[cat]['social']]:
            return 'social'
    return None

def get_reviewers_for_activity(activity):
    User = get_user_model()  # ✅ To'g'ri foydalanuvchi modeli
    from .models import Reviewer

    section = get_section_for_activity_type(activity.activity_type)
    if not section:
        return User.objects.none()

    field = f'can_review_employee_{section}'

    return User.objects.filter(reviewer__isnull=False, **{f'reviewer__{field}': True})



STUDENT_MEZON_CATEGORIES = {
    'taught': [
        ('attendance', 'Dars mashg`ulotlariga davomati', 30, False),
        ('grades', 'Fanlarni o‘zlashtirishi', 30, False),
        ('student_mobility', 'Akademik mobiligi', 20, True),
        ('circle_participation', 'To`garaklarda ishtrok etishi (fan koordinatori rahbarligida)', 20, False),
    ],
    'research': [
        ('student_oak', '(OAK) tasarrufidagi indeksatsiya qilingan nashrlarda maqola chop etish, shu jumladan hammualiflikda', 30, True),
        ('olympiad_award', 'Respublika fan olimpiadasida sovrin, o`rin olishi va ilmiy amaliy anjumanlarda ma`ruza bilan ishtrok etib sovrinli o`rin egallashi', 40, True),
        ('language_cert', 'Til bilish darajasi mavjudligi: IELTS, CEFR, TOEFL, TOPIK,  Türkçe Yeterlilik Belgesi (TÖMER, Yunus Emre Enstitüsü)', 30, True),
    ],
    'social': [
        ('moral_events', 'Ma`naviy-ma`rifiy tadbirlarda faol ishtrok etish / Shaxsiy intizom', 30, False),
        ('initiative_award', '“5 tashabbus”, Kitobxonlik, Zakovat, sport, san’at, teatr IT va boshqa tanlovlarda  ishtrok etib sovrinli o`rin egallashi (I / II / III o`rin) ', 30, True),
        ('social_media', 'Ijtimoiy tarmoqlardagi faolligi (reels, post, stories)', 40, True),
    ]
}
