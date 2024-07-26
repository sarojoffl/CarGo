from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiration = models.DateTimeField(null=True, blank=True)
    watchlist = models.ManyToManyField('Car', related_name='watchlisted_by', blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.email})"

class Car(models.Model):
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    images = models.ManyToManyField('CarImage', related_name='cars', blank=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_available_for_sale = models.BooleanField(default=True)
    is_available_for_rent = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"

class Sale(models.Model):
    car = models.ForeignKey(Car, related_name='sales', on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    sale_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Sale of {self.car} to {self.buyer} for Rs. {self.amount}"

class Rental(models.Model):
    car = models.ForeignKey(Car, related_name='rentals', on_delete=models.CASCADE)
    renter = models.ForeignKey(User, on_delete=models.CASCADE)
    rental_start_date = models.DateTimeField()
    rental_end_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cancellation_reason = models.CharField(max_length=255, blank=True, null=True)
    cancellation_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Rental of {self.car} to {self.renter} from {self.rental_start_date} to {self.rental_end_date} for Rs. {self.amount}"

class PaymentDetails(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_details')
    car = models.ForeignKey('Car', on_delete=models.CASCADE, related_name='payment_details')
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=50)
    is_verified = models.BooleanField(default=False)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} via {self.payment_method} for {self.car}"

class CarImage(models.Model):
    image = models.ImageField(upload_to='car_images/')
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.description or f"Image {self.pk}"

