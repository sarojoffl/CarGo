from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.contrib.auth import get_user_model

from decimal import Decimal
import uuid
import requests

from .models import Car, Rental, Sale, CarImage
from .forms import CarForm, CarImageFormSet

User = get_user_model()

def index(request):
    return render(request, 'index.html')

def sales(request):
    cars_for_sale = Car.objects.filter(is_available_for_sale=True)
    return render(request, 'sales.html', {'cars_for_sale': cars_for_sale})

def rentals(request):
    cars_for_rent = Car.objects.filter(is_available_for_rent=True)
    return render(request, 'rentals.html', {'cars_for_rent': cars_for_rent}) 
        
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    discounted_price = car.price - (car.price * car.discount / 100) if car.discount else car.price
    
    context = {
        'car': car,
        'discounted_price': discounted_price
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

@user_passes_test(lambda u: u.is_superuser)
def car_create(request):
    if request.method == "POST":
        form = CarForm(request.POST)
        formset = CarImageFormSet(request.POST, request.FILES, queryset=CarImage.objects.none())
        if form.is_valid() and formset.is_valid():
            car = form.save()
            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    description = form.get('description', '')
                    CarImage.objects.create(image=image, description=description, cars=car)
            return redirect('car_list')
    else:
        form = CarForm()
        formset = CarImageFormSet(queryset=CarImage.objects.none())
    return render(request, 'car_form.html', {'form': form, 'formset': formset})

@user_passes_test(lambda u: u.is_superuser)
def car_update(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if request.method == "POST":
        form = CarForm(request.POST, instance=car)
        formset = CarImageFormSet(request.POST, request.FILES, queryset=car.images.all())
        if form.is_valid() and formset.is_valid():
            form.save()
            for form in formset:
                if form.cleaned_data:
                    image = form.cleaned_data['image']
                    description = form.cleaned_data.get('description', '')
                    if form.cleaned_data.get('DELETE'):
                        form.instance.delete()
                    else:
                        form.instance.cars.add(car)
                        form.instance.image = image
                        form.instance.description = description
                        form.instance.save()
            return redirect('car_list')
    else:
        form = CarForm(instance=car)
        formset = CarImageFormSet(queryset=car.images.all())
    return render(request, 'car_form.html', {'form': form, 'formset': formset})

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    new_users = User.objects.order_by('-date_joined')[:4]
    context = {'new_users': new_users}
    return render(request, 'admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
def car_list(request):
    cars = Car.objects.all()
    return render(request, 'car_list.html', {'cars': cars})

@user_passes_test(lambda u: u.is_superuser)
def car_delete(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if request.method == "POST":
        car.delete()
        return redirect('car_list')
    return render(request, 'car_confirm_delete.html', {'car': car})

@user_passes_test(lambda u: u.is_superuser)
def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

def checkout(request):
    car_id = request.GET.get('car_id')
    transaction_type = request.GET.get('type', 'sale')
    rental_days = int(request.GET.get('rental_days', 1))
    
    car = get_object_or_404(Car, id=car_id)
    
    rental_rate = Decimal('0.01')
    rental_price_per_day = car.price * rental_rate
    total_rental_price = rental_price_per_day * rental_days
    
    if transaction_type == 'rent':
        total_price = total_rental_price
    else:
        total_price = car.price - (car.price * (car.discount / 100)) if car.discount else car.price
    
    context = {
        'car': car,
        'total_price': total_price,
        'transaction_type': transaction_type,
        'rental_price_per_day': rental_price_per_day,
        'rental_days': rental_days
    }
    return render(request, 'checkout.html', context)

@login_required
def process_checkout(request):
    if request.method == 'POST':
        user = request.user
        car_id = request.POST.get('car_id')
        car = get_object_or_404(Car, pk=car_id)

        firstname = request.POST['firstname']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        city = request.POST['city']
        payment_method = request.POST['paymentMethod']
        transaction_type = request.POST['transaction_type']

        if transaction_type == 'rent':
            startdate = request.POST['startdate']
            enddate = request.POST['enddate']
            rental = Rental(
                car=car,
                renter=user,
                rental_start_date=startdate,
                rental_end_date=enddate,
                is_active=True
            )
            rental.save()
            car.is_available_for_rent = False
            car.save()
        else:
            pickupdate = request.POST['pickupdate']
            sale = Sale(
                car=car,
                buyer=user,
                sale_date=timezone.now()
            )
            sale.save()
            car.is_available_for_sale = False
            car.is_available_for_rent = False
            car.save()

        same_address = request.POST.get('sameadr', False) == 'on'
        
        active_rentals = Rental.objects.filter(car=car, is_active=True)
        for rental in active_rentals:
            rental.is_active = False
            rental.rental_end_date = timezone.now()
            rental.save()

        context = {
                'firstname': firstname,
                'email': email,
                'phone': phone,
                'address': address,
                'city': city,
                'payment_method': payment_method,
                'transaction_type': transaction_type,
                'startdate': startdate if transaction_type == 'rent' else None,
                'enddate': enddate if transaction_type == 'rent' else None,
                'pickupdate': pickupdate if transaction_type == 'sale' else None,
        }                    
        
        return render(request, 'success.html', context)

    return render(request, 'checkout.html')

def home(request):
    id = uuid.uuid4()
    return render(request, 'khalti.html', {'uuid': id})

def initkhalti(request):
    if request.method == 'POST':
        url = "https://a.khalti.com/api/v2/epayment/initiate/"
        return_url = request.POST.get('return_url')
        amount = request.POST.get('amount')
        purchase_order_id = request.POST.get('purchase_order_id')
        user = request.user

        if not all([return_url, amount, purchase_order_id]):
            return HttpResponseBadRequest("Missing required parameters")

        payload = {
            "return_url": return_url,
            "website_url": "http://127.0.0.1:8000",
            "amount": amount,
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": "test",
            "customer_info": {
                "name": user.first_name,
                "email": user.email,
                "phone": user.phone_number
            }
        }

        headers = {
            'Authorization': 'Key your_live_secret_key',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()

            if response.status_code == 200 and 'payment_url' in response_data:
                return redirect(response_data['payment_url'])
            else:
                return JsonResponse(response_data, status=response.status_code)

        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return HttpResponseBadRequest("Invalid request method")

def verifyKhalti(request):
    if request.method == 'GET':
        url = "https://a.khalti.com/api/v2/epayment/lookup/"
        pidx = request.GET.get('pidx')

        if not pidx:
            return HttpResponseBadRequest("Missing required parameters")

        headers = {
            'Authorization': 'Key your_live_secret_key',
            'Content-Type': 'application/json',
        }

        payload = {'pidx': pidx}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()

            if response.status_code == 200:
                return JsonResponse(response_data)
            else:
                return JsonResponse(response_data, status=response.status_code)

        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return HttpResponseBadRequest("Invalid request method")
