# hemis_oauth/urls.py
from django.urls import path
from hemis_oauth import views

# app_name = "hemis_oauth"

urlpatterns = [
    path("select/", views.select_login, name="select"),
    path("login/<str:profile>/", views.login_start, name="login_start_profile"),  # profile: employee|student
    path("callback/", views.callback, name="callback_profile"),
    path('logout/', views.logout_view, name='logout'),
]
