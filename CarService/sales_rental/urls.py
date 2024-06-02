# urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path('register/', views.register, name='register'),
    path('confirm_email/', views.confirm_email, name='confirm_email'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
]

