from django.urls import path
from . import views
from . import auth_views as custom_auth_views
from . import admin_views
from . import payment_views

urlpatterns = [
    path('', views.index, name='index'),
    path('login_register/', custom_auth_views.login_register_view, name='login_register'),
    path('logout/', custom_auth_views.logout_view, name='logout'),
    path('confirm_email/', custom_auth_views.confirm_email, name='confirm_email'),
    path('forgot_password/', custom_auth_views.forgot_password, name='forgot_password'),
    path('verify_otp/', custom_auth_views.verify_otp, name='verify_otp'),
    path('reset_password/', custom_auth_views.reset_password, name='reset_password'),
    path('resend_otp/', custom_auth_views.resend_otp, name='resend_otp'),
    path('search/', views.search, name='search'),
    path('sales/', views.sales, name='sales'),
    path('rentals/', views.rentals, name='rentals'),
    path('watchlist/', views.view_watchlist, name='view_watchlist'),
    path('toggle_watchlist/<int:car_id>/', views.toggle_watchlist, name='toggle_watchlist'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('cars/add/', admin_views.car_create, name='car_create'),
    path('cars/<int:car_id>/edit/', admin_views.car_update, name='car_update'),
    path('cars/<int:car_id>/delete/', admin_views.car_delete, name='car_delete'),
    path('cars/', admin_views.car_list, name='car_list'),
    path('car_history/<int:car_id>/', admin_views.car_history, name='car_history'),
    path('rental_history/', admin_views.rental_history, name='rental_history'),
    path('sales_history/', admin_views.sales_history, name='sales_history'),
    path('users/', admin_views.user_list, name='user_list'),
    path('user/<int:user_id>/edit/', admin_views.user_edit, name='user_edit'),
    path('user/<int:user_id>/delete/', admin_views.user_delete, name='user_delete'),
    path('admin_dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('checkout/', payment_views.checkout, name='checkout'),
    path('process_checkout/', payment_views.process_checkout, name='process_checkout'),
    path('initiate/', payment_views.initkhalti, name='initiate'),
    path('verify/', payment_views.verifyKhalti, name='verify'),
]
