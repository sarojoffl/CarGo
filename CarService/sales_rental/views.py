from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import get_user_model

from decimal import Decimal

from .models import Car, Rental, Sale, CarImage
from .forms import UserForm, CarForm, CarImageFormSet

User = get_user_model()

def index(request):
    return render(request, 'index.html')

def search(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Car.objects.filter(model__icontains=query) | Car.objects.filter(make__icontains=query) | Car.objects.filter(description__icontains=query)
    return render(request, 'search_results.html', {'results': results, 'query': query})
    
def sales(request):
    cars_for_sale = Car.objects.filter(is_available_for_sale=True)
    return render(request, 'sales.html', {'cars_for_sale': cars_for_sale})

def rentals(request):
    cars_for_rent = Car.objects.filter(is_available_for_rent=True)
    return render(request, 'rentals.html', {'cars_for_rent': cars_for_rent}) 
        
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    if car.discount:
        discounted_price = car.price - (car.price * car.discount / 100)
    else:
        discounted_price = car.price
    
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
        # messages.success(request, f'{car.make} {car.model} has been removed from your watchlist.')
    else:
        request.user.watchlist.add(car)
        # messages.success(request, f'{car.make} {car.model} has been added to your watchlist.')
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
        formset = CarImageFormSet(request.POST, request.FILES, queryset=CarImage.objects.filter(cars=car))
        if form.is_valid() and formset.is_valid():
            car = form.save()
            for image_form in formset:
                if image_form.cleaned_data:
                    image = image_form.cleaned_data.get('image')
                    description = image_form.cleaned_data.get('description')
                    if image_form.cleaned_data.get('DELETE'):
                        image_form.instance.delete()
                    else:
                        image_instance = image_form.save(commit=False)
                        image_instance.description = description
                        image_instance.save()
                        image_instance.cars.add(car)
            return redirect('car_list')
    else:
        form = CarForm(instance=car)
        formset = CarImageFormSet(queryset=CarImage.objects.filter(cars=car))
    return render(request, 'car_form.html', {'form': form, 'formset': formset})
            
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    total_cars = Car.objects.count()
    cars_for_sale = Car.objects.filter(is_available_for_sale=True).count()
    cars_for_rent = Car.objects.filter(is_available_for_rent=True).count()
    new_users = User.objects.order_by('-date_joined')[:4]
    recent_rentals = Rental.objects.order_by('-rental_start_date')[:5]
    recent_sales = Sale.objects.order_by('-sale_date')[:5]

    context = {
        'total_cars': total_cars,
        'cars_for_sale': cars_for_sale,
        'cars_for_rent': cars_for_rent,
        'new_users': new_users,
        'recent_rentals': recent_rentals,
        'recent_sales': recent_sales,
    }

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

@user_passes_test(lambda u: u.is_superuser)
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'user_form.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'user_confirm_delete.html', {'user': user})

@login_required
def checkout(request):
    car_id = request.GET.get('car_id')
    transaction_type = request.GET.get('type', 'sale')
    car = get_object_or_404(Car, id=car_id)
    
    if transaction_type == 'rent':
        rental_days = int(request.GET.get('rental_days', 1))
        rental_rate = Decimal('0.01')
        rental_price_per_day = car.price * rental_rate
        total_price = rental_price_per_day * rental_days
    else:
        if car.discount:
            total_price = car.price - (car.price * car.discount / 100)
        else:
            total_price = car.price
    
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
        car = Car.objects.get(pk=car_id)

        # Common form data
        firstname = request.POST['firstname']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        city = request.POST['city']
        payment_method = request.POST['paymentMethod']
        transaction_type = request.POST['transaction_type']

        # Different handling based on transaction type
        if transaction_type == 'rent':
            startdate = request.POST['startdate']
            enddate = request.POST['enddate']
            # Create Rental record
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

        # Implement your checkout processing logic here

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
        
        # Redirect to a success page or show a success message
        return render(request, 'success.html', context)

    return render(request, 'checkout.html')
    
@user_passes_test(lambda u: u.is_superuser)
def car_history(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    sales = car.sales.all()
    rentals = car.rentals.all()

    context = {
        'car': car,
        'sales': sales,
        'rentals': rentals
    }
    return render(request, 'car_history.html', context)
    
@user_passes_test(lambda u: u.is_superuser)
def rental_history(request):
    rental_history = Rental.objects.order_by('-rental_start_date')
    return render(request, 'rental_history.html', {'rental_history': rental_history})

@user_passes_test(lambda u: u.is_superuser)
def sales_history(request):
    sales_history = Sale.objects.order_by('-sale_date')
    return render(request, 'sales_history.html', {'sales_history': sales_history})

