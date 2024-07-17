from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiration = models.DateTimeField(null=True, blank=True)
    watchlist = models.ManyToManyField('Car', related_name='watchlisted_by', blank=True)

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
    colors = models.ManyToManyField('CarColor', related_name='cars', blank=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"

class Sale(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    sale_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale of {self.car} to {self.buyer}"

class Rental(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    renter = models.ForeignKey(User, on_delete=models.CASCADE)
    rental_start_date = models.DateTimeField()
    rental_end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Rental of {self.car} to {self.renter} from {self.rental_start_date} to {self.rental_end_date}"

class CarImage(models.Model):
    image = models.ImageField(upload_to='car_images/')
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.description or f"Image {self.pk}"

class CarColor(models.Model):
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.color

