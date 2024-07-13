from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.utils import timezone
from .models import User, Car, Rental, CarColor, Sale
from .utils import generate_otp, send_otp_email, is_password_valid
from .forms import CarForm, RentalForm
from decimal import Decimal

def index(request):
    cars_for_sale = Car.objects.filter(is_available_for_sale=True)
    cars_for_rent = Car.objects.filter(is_available_for_rent=True)
    context = {
        'cars_for_sale': cars_for_sale,
        'cars_for_rent': cars_for_rent,
    }
    return render(request, 'index.html', context)
