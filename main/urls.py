from django.urls import path
from . import views
from django.shortcuts import redirect



urlpatterns = (
    path('', views.home_view, name='home'),
    path('yuklama/', views.yuklama_view, name='yuklama'),
    # path('rating/', views.rating_form_view, name='rating_form'),
    path('taught/', views.taught_view, name='taught'),
    path('research/', views.research_view, name='research'),
    path('social/', views.social_view, name='social'),
    path('mezon/<str:activity_type>/', views.mezon_detail_view, name='mezon_detail'),
    path('mezon/<str:activity_type>/add/', views.add_activity_view, name='add_activity'),

    # Tekshiruvchilar
    path('reviewer/', views.reviewer_dashboard, name='reviewer_dashboard'),
    path('help_teacher/', views.help_teacher, name='help_teacher'),
    path('help_student/', views.help_student, name='help_student'),
    path('review/<int:activity_id>/', views.review_activity, name='review_activity'),
    path('student-reviewer/', views.student_reviewer_dashboard, name='student_reviewer_dashboard'),
    path('review-student/<int:activity_id>/', views.review_student_activity, name='review_student_activity'),
path('assign-points/<int:activity_id>/', views.assign_points_to_student_activity, name='assign_points_to_student_activity'),

    # --- Talabalar uchun yangi URLlar ---
    path('student/taught/', views.student_taught_view, name='student_taught'),
    path('student/research/', views.student_research_view, name='student_research'),
    path('student/social/', views.student_social_view, name='student_social'),
    path('student/<str:section>/<str:activity_type>/', views.student_mezon_detail_view, name='student_mezon_detail'),
    path('student/<str:section>/<str:activity_type>/add/', views.student_add_activity_view,
         name='student_add_activity'),

)