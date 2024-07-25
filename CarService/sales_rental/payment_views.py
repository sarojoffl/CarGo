from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.utils.http import urlencode
from django.conf import settings
from django.contrib.auth import get_user_model
import requests
import uuid
from datetime import datetime
from decimal import Decimal
from .models import Car, PaymentDetails, Rental, Sale
from .utils import update_database_after_payment

User = get_user_model()

@login_required
def checkout(request):
    car_id = request.GET.get('car_id')
    transaction_type = request.GET.get('type', 'sale')
    car = get_object_or_404(Car, id=car_id)
    rental_days = int(request.GET.get('rental_days', 1)) if transaction_type == 'rent' else None
    rental_rate = Decimal('0.01') if transaction_type == 'rent' else None
    rental_price_per_day = car.price * rental_rate if transaction_type == 'rent' else None
    total_price = rental_price_per_day * rental_days if transaction_type == 'rent' else car.price - (car.price * car.discount / 100) if car.discount else car.price
    context = {
        'car': car,
        'total_price': total_price,
        'transaction_type': transaction_type,
        'rental_price_per_day': rental_price_per_day if transaction_type == 'rent' else None,
        'rental_days': rental_days if transaction_type == 'rent' else None
    }
    return render(request, 'checkout.html', context)

@login_required
def process_checkout(request):
    if request.method == 'POST':
        user = request.user
        car_id = request.POST.get('car_id')
        car = get_object_or_404(Car, pk=car_id)

        request.session['car_id'] = car_id
        request.session['firstname'] = request.POST['firstname']
        request.session['email'] = request.POST['email']
        request.session['phone'] = request.POST['phone']
        request.session['address'] = request.POST['address']
        request.session['city'] = request.POST['city']
        request.session['paymentMethod'] = request.POST['paymentMethod']
        request.session['transaction_type'] = request.POST['transaction_type']
        request.session['same_address'] = request.POST.get('sameadr', False) == 'on'

        # Calculate total price based on transaction type
        if request.session['transaction_type'] == 'rent':
            request.session['startdate'] = request.POST['startdate']
            request.session['enddate'] = request.POST['enddate']
            rental_days = (datetime.strptime(request.session['enddate'], '%Y-%m-%dT%H:%M') - datetime.strptime(request.session['startdate'], '%Y-%m-%dT%H:%M')).days
            rental_price_per_day = Decimal(car.price * Decimal('0.01'))
            total_price = rental_price_per_day * rental_days
        else:
            total_price = car.price - (car.price * car.discount / 100) if car.discount else car.price
            request.session['pickupdate'] = request.POST['pickupdate']

        request.session['total_price'] = str(total_price)

        if request.session['paymentMethod'] == 'khalti':
            base_url = reverse('initiate')
            query_params = urlencode({
                'return_url': request.build_absolute_uri(reverse('verify')),
                'amount': int(total_price * 100),
                'purchase_order_id': str(uuid.uuid4())
            })
            full_url = f"{base_url}?{query_params}"
            return redirect(full_url)

    return render(request, 'checkout.html')

def initkhalti(request):
    if request.method == 'GET':
        url = "https://a.khalti.com/api/v2/epayment/initiate/"
        return_url = request.GET.get('return_url')
        amount = request.GET.get('amount')
        purchase_order_id = request.GET.get('purchase_order_id')
        user = request.user

        if not all([return_url, amount, purchase_order_id]):
            return HttpResponseBadRequest("Missing required parameters")

        payload = {
            "return_url": return_url,
            "website_url": "http://127.0.0.1:8000",
            "amount": amount,
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": "Car Purchase/Rental",
            "customer_info": {
                "name": request.session['firstname'],
                "email": request.session['email'],
                "phone": request.session['phone']
            }
        }

        headers = {
            'Authorization': "Key c54d590299d843a788b6bd49ff6da91d",
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
            "Authorization": "Key c54d590299d843a788b6bd49ff6da91d",
            'Content-Type': 'application/json',
        }

        payload = {'pidx': pidx}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()
            if response.status_code == 200 and response_data.get('status') == 'Completed':
                # Update the database based on the transaction type stored in session
                transaction_id = response_data.get('transaction_id')
                user = request.user
                amount = response_data['total_amount'] / 100  # Khalti returns amount in paisa
                
                purchase_order_id = request.session.get('car_id')
                car = Car.objects.get(id=purchase_order_id)
                
                payment_details = PaymentDetails(
                    user=user,
                    car=car,
                    transaction_id=transaction_id,
                    amount=amount,
                    payment_method='Khalti',
                    transaction_type=transaction_type,
                    is_verified=True
                )
                payment_details.save()

                purchase_order_id = request.session.get('car_id')
                car = Car.objects.get(id=purchase_order_id)
                transaction_type = request.session.get('transaction_type')
                update_database_after_payment(transaction_type, car, user, request.session)

                context = {
                    'firstname': request.session['firstname'],
                    'email': request.session['email'],
                    'phone': request.session['phone'],
                    'address': request.session['address'],
                    'city': request.session['city'],
                    'payment_method': 'Khalti',
                    'transaction_type': transaction_type,
                    'total_price': request.session['total_price'],
                    'same_address': request.session['same_address'],
                    'startdate': request.session.get('startdate', None),
                    'enddate': request.session.get('enddate', None),
                    'pickupdate': request.session.get('pickupdate', None),
                    'transaction_id': transaction_id,
                    'car_model': car.model,
                    'car_make': car.make,
                    'car_year': car.year,
                }

                return render(request, 'success.html', context)
            else:
                return JsonResponse(response_data, status=response.status_code)
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return HttpResponseBadRequest("Invalid request method")

