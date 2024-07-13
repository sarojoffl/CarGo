# urls.py

from django.urls import path
from . import views
from . import index_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', index_view.index, name='index'),
    path('login_register/', views.login_register_view, name='login_register'),
    path("logout", views.logout_view, name="logout"),
    path('confirm_email/', views.confirm_email, name='confirm_email'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),   
    path('watchlist/', views.view_watchlist, name='view_watchlist'),
    path('toggle_watchlist/<int:car_id>/', views.toggle_watchlist, name='toggle_watchlist'),    
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),    
    path('cars/add/', views.car_create, name='car_create'),
    path('cars/<int:car_id>/edit/', views.car_update, name='car_update'),
    path('cars/<int:car_id>/delete/', views.car_delete, name='car_delete'),
    path('manage_rentals/', views.manage_rentals, name='manage_rentals'),    
    path('checkout/', views.checkout, name='checkout'),
    path('process_checkout/', views.process_checkout, name='process_checkout'),
]
