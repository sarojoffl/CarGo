from background_task import background
from django.core.mail import send_mail
from .models import Rental

@background(schedule=60) 
def check_and_update_rental_status():
    rentals = CarRental.objects.filter(status='active')
    for rental in rentals:
        rental.status = 'updated'
        rental.save()

