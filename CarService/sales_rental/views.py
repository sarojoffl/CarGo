from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from .models import User
import uuid
from datetime import timedelta
from django.conf import settings
from django.utils.crypto import get_random_string

def index(request):
    return render(request, "index.html")

def login_view(request):
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.email_confirmed:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                messages.error(request, "Please confirm your email before logging in.")
                return redirect('confirm_email')
        else:
            messages.error(request, "Invalid username and/or password.")
            return redirect('login')
    else:
        return render(request, "login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def generate_otp():
    return get_random_string(length=6, allowed_chars='0123456789')

def send_otp(user):
    user.otp = generate_otp()
    user.otp_expiration = timezone.now() + timedelta(minutes=10)
    user.save()
    subject = 'Your OTP Code'
    message = f'Use this OTP to confirm your email: {user.otp}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            messages.error(request, "Passwords must match.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('register')

        try:
            user = User.objects.create_user(username, email, password)
            send_otp(user)
            messages.success(request, "Check your email for the OTP code to confirm your email.")
            return redirect('confirm_email')
        except IntegrityError:
            messages.error(request, "Username already taken.")
            return redirect('register')
    else:
        return render(request, "register.html")

def confirm_email(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        try:
            user = User.objects.get(otp=otp)
            if user.email_confirmed:
                messages.info(request, "Email already confirmed.")
                return redirect('login')

            if timezone.now() > user.otp_expiration:
                messages.error(request, "OTP has expired.")
                send_otp(user)
                messages.info(request, "A new OTP has been sent to your email.")
                return redirect('confirm_email')

            user.email_confirmed = True
            user.otp = None
            user.otp_expiration = None
            user.save()
            login(request, user)
            messages.success(request, "Email confirmed successfully.")
            return HttpResponseRedirect(reverse("login"))
        except User.DoesNotExist:
            messages.error(request, "Invalid OTP.")
            return redirect('confirm_email')
    return render(request, 'confirm_email.html')

