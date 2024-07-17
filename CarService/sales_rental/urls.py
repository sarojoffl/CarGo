from django.urls import path
from . import views
from . import auth_views as custom_auth_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('login_register/', custom_auth_views.login_register_view, name='login_register'),
    path('logout/', custom_auth_views.logout_view, name='logout'),
    path('confirm_email/', custom_auth_views.confirm_email, name='confirm_email'),
    path('forgot_password/', custom_auth_views.forgot_password, name='forgot_password'),
    path('verify_otp/', custom_auth_views.verify_otp, name='verify_otp'),
    path('reset_password/', custom_auth_views.reset_password, name='reset_password'),
    path('resend_otp/', custom_auth_views.resend_otp, name='resend_otp'),
    path('sales/', views.sales, name='sales'),
    path('rentals/', views.rentals, name='rentals'),
    path('watchlist/', views.view_watchlist, name='view_watchlist'),
    path('toggle_watchlist/<int:car_id>/', views.toggle_watchlist, name='toggle_watchlist'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('cars/add/', views.car_create, name='car_create'),
    path('cars/<int:car_id>/edit/', views.car_update, name='car_update'),
    path('cars/<int:car_id>/delete/', views.car_delete, name='car_delete'),
    path('cars/', views.car_list, name='car_list'),
    path('users/', views.user_list, name='user_list'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('checkout/', views.checkout, name='checkout'),
    path('process_checkout/', views.process_checkout, name='process_checkout'),
]

