from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.conf import settings
from .models import Car, Sale, Rental
from .forms import CarFilterForm, UserForm
from django.db import models
from datetime import datetime
from urllib.parse import urlencode

User = get_user_model()

def index(request):
    return render(request, 'index.html')

def search(request):
    query = request.GET.get('q')
    results = Car.objects.none()
    form = CarFilterForm(request.GET)
    
    if query:
        results = Car.objects.filter(
            models.Q(model__icontains=query) |
            models.Q(make__icontains=query) |
            models.Q(year__icontains=query) |
            models.Q(description__icontains=query)
        )
        
    if form.is_valid():
        if form.cleaned_data['make']:
            results = results.filter(make__icontains=form.cleaned_data['make'])
        if form.cleaned_data['model']:
            results = results.filter(model__icontains=form.cleaned_data['model'])
        if form.cleaned_data['year']:
            results = results.filter(year=form.cleaned_data['year'])
        if form.cleaned_data['min_price']:
            results = results.filter(price__gte=form.cleaned_data['min_price'])
        if form.cleaned_data['max_price']:
            results = results.filter(price__lte=form.cleaned_data['max_price'])

    return render(request, 'search_results.html', {'results': results, 'query': query, 'form': form})
    
def sales(request):
    cars_for_sale = Car.objects.filter(is_available_for_sale=True)
    return render(request, 'sales.html', {'cars_for_sale': cars_for_sale})

def rentals(request):
    cars_for_rent = Car.objects.filter(is_available_for_rent=True)
    return render(request, 'rentals.html', {'cars_for_rent': cars_for_rent}) 
        
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    discounted_price = car.price - (car.price * car.discount / 100) if car.discount else car.price
    
    # Check if the car is currently rented
    current_rental = Rental.objects.filter(car=car, is_active=True).first()
    is_rented = current_rental is not None
    
    # Check if the car is sold
    is_sold = not car.is_available_for_sale    
    
    context = {
        'car': car,
        'discounted_price': discounted_price,
        'is_rented': is_rented,
        'current_rental': current_rental,
        'is_sold': is_sold
    }
    return render(request, 'car_detail.html', context)

@login_required
def view_watchlist(request):
    user_watchlist = request.user.watchlist.all()
    return render(request, 'watchlist.html', {'watchlist': user_watchlist})

@login_required
def toggle_watchlist(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if car in request.user.watchlist.all():
        request.user.watchlist.remove(car)
    else:
        request.user.watchlist.add(car)
    return redirect('car_detail', car_id=car_id)

@login_required
def user_history(request):
    user_sales = Sale.objects.filter(buyer=request.user)
    user_rentals = Rental.objects.filter(renter=request.user)
    return render(request, 'user_history.html', {'user_sales': user_sales, 'user_rentals': user_rentals})

@login_required
def manage_profile(request):
    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('manage_profile')
    else:
        form = UserForm(instance=request.user)
    return render(request, 'manage_profile.html', {'form': form})

