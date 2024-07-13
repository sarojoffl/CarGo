# sales_rental/middleware.py
from django.utils import timezone
from sales_rental.models import Rental

class RentalCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.update_rentals()
        response = self.get_response(request)
        return response

    def update_rentals(self):
        now = timezone.now()
        active_rentals = Rental.objects.filter(rental_end_date__lt=now, is_active=True)
        for rental in active_rentals:
            rental.is_active = False
            rental.car.is_available_for_rent = True
            rental.car.save()
            rental.save()

