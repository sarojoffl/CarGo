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

def login_register_view(request):
    form_mode = 'signin'  # Default mode

    if request.method == "POST":
        if 'signin' in request.POST:
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.email_confirmed:
                    login(request, user)
                    if user.is_superuser:
                        return redirect('admin_dashboard')
                    else:
                        return redirect('index')
                else:
                    messages.error(request, "Please confirm your email before logging in.")
                    return redirect('confirm_email')
            else:
                messages.error(request, "Invalid username and/or password.", extra_tags='signin')
                return render(request, 'login_register.html', {'form_mode': 'signin'})

        elif 'signup' in request.POST:
            username = request.POST["username"]
            email = request.POST["email"]
            password = request.POST["password"]
            confirmation = request.POST["confirmation"]

            if password != confirmation:
                messages.error(request, "Passwords must match.", extra_tags='signup')
                return render(request, 'login_register.html', {'form_mode': 'signup'})

            is_valid, validation_message = is_password_valid(password)
            if not is_valid:
                messages.error(request, validation_message, extra_tags='signup')
                return render(request, 'login_register.html', {'form_mode': 'signup'})

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already in use.", extra_tags='signup')
                return render(request, 'login_register.html', {'form_mode': 'signup'})

            try:
                user = User.objects.create_user(username, email, password)
                user.email_confirmed = False
                user.otp = generate_otp()
                user.otp_expiration = timezone.now() + timezone.timedelta(minutes=10)
                user.save()
                send_otp_email(user, 'Your OTP Code', 'confirm your email')
                messages.success(request, "Check your email for the OTP code to confirm your email.")
                return redirect('confirm_email')
            except IntegrityError:
                messages.error(request, "Username already taken.", extra_tags='signup')
                return render(request, 'login_register.html', {'form_mode': 'signup'})

    return render(request, "login_register.html", {'form_mode': form_mode})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def confirm_email(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        try:
            user = User.objects.get(otp=otp)
            if user.email_confirmed:
                messages.info(request, "Email already confirmed.")
                return redirect('login_register')

            if timezone.now() > user.otp_expiration:
                messages.error(request, "OTP has expired.")
                user.otp = generate_otp()  # Regenerate OTP
                user.otp_expiration = timezone.now() + timezone.timedelta(minutes=10)
                user.save()
                send_otp_email(user, 'Your OTP Code', 'confirm your email')
                messages.info(request, "A new OTP has been sent to your email.")
                return redirect('confirm_email')

            user.email_confirmed = True
            user.otp = None
            user.otp_expiration = None
            user.save()
            messages.success(request, "Email confirmed successfully. Please log in.")
            return redirect('login_register')
        except User.DoesNotExist:
            messages.error(request, "Invalid OTP.")
            return redirect('confirm_email')
    return render(request, 'confirm_email.html')

def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]
        try:
            user = User.objects.get(email=email)
            user.otp = generate_otp()  # Generate OTP
            user.otp_expiration = timezone.now() + timezone.timedelta(minutes=10)
            user.save()
            send_otp_email(user, 'Password Reset OTP', 'reset your password')
            messages.success(request, "Check your email for the OTP code to reset your password.")
            request.session['user_id'] = user.id
            return redirect('verify_otp')
        except User.DoesNotExist:
            messages.error(request, "Email not found.")
            return redirect('forgot_password')
    return render(request, "forgot_password.html")

def verify_otp(request):
    if request.method == "POST":
        otp = request.POST['otp']
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "Session expired. Please try again.")
            return redirect('forgot_password')
        
        try:
            user = User.objects.get(id=user_id, otp=otp)
            if timezone.now() > user.otp_expiration:
                messages.error(request, "OTP has expired.")
                user.otp = generate_otp()  # Regenerate OTP
                user.otp_expiration = timezone.now() + timezone.timedelta(minutes=10)
                user.save()
                send_otp_email(user, 'Password Reset OTP', 'reset your password')
                messages.info(request, "A new OTP has been sent to your email.")
                return redirect('verify_otp')
            
            request.session['otp_verified'] = True
            return redirect('reset_password')
        except User.DoesNotExist:
            messages.error(request, "Invalid OTP.")
            return redirect('verify_otp')
    return render(request, "verify_otp.html")

def reset_password(request):
    if not request.session.get('otp_verified'):
        messages.error(request, "OTP verification required.")
        return redirect('forgot_password')

    if request.method == "POST":
        new_password = request.POST['new_password']
        confirmation = request.POST['confirmation']
        
        if new_password != confirmation:
            messages.error(request, "Passwords must match.")
            return redirect('reset_password')

        # Validate the new password
        is_valid, validation_message = is_password_valid(new_password)
        if not is_valid:
            messages.error(request, validation_message)
            return redirect('reset_password')

        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "Session expired. Please try again.")
            return redirect('forgot_password')

        try:
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.otp = None
            user.otp_expiration = None
            user.save()
            messages.success(request, "Password reset successfully. Please log in.")
            return redirect('login_register')
        except User.DoesNotExist:
            messages.error(request, "An error occurred. Please try again.")
            return redirect('reset_password')
    return render(request, "reset_password.html")
    
def resend_otp(request):
    if request.method == "POST":
        user_id = request.session.get('user_id')
        
        if not user_id:
            messages.error(request, "Session expired. Please try again.")
            return redirect('forgot_password')
        
        try:
            user = User.objects.get(id=user_id)
            user.otp = generate_otp()
            user.otp_expiration = timezone.now() + timezone.timedelta(minutes=10)
            user.save()
            
            send_otp_email(user, 'Verify Your OTP', 'verify your action')
            
            messages.info(request, "A new OTP has been sent to your email.")
            
            if 'verify_otp' in request.META.get('HTTP_REFERER', ''):
                return redirect('verify_otp')
            else:
                return redirect('confirm_email')
        
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('forgot_password')
    
    return render(request, "verify_otp.html")
    
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
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('car_list')
    else:
        form = CarForm()
    return render(request, 'car_form.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def car_update(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if request.method == "POST":
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            return redirect('car_detail', car_id=car.id)
    else:
        form = CarForm(instance=car)
    return render(request, 'car_form.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def car_delete(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if request.method == "POST":
        car.delete()
        return redirect('car_list')
    return render(request, 'car_confirm_delete.html', {'car': car})

@user_passes_test(lambda u: u.is_superuser)
def manage_rentals(request):
    rentals = Rental.objects.all()
    return render(request, 'manage_rentals.html', {'rentals': rentals})    

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
        
        
        active_rentals = Rental.objects.filter(car=car, is_active=True)
        for rental in active_rentals:
            rental.is_active = False
            rental.rental_end_date = timezone.now()
            rental.save()

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
