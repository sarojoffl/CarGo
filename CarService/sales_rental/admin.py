from django.contrib import admin
from .models import User, Car, Sale,Rental, CarImage, PaymentDetails

admin.site.register(User)
admin.site.register(Car)
admin.site.register(Sale)
admin.site.register(Rental)
admin.site.register(CarImage)
admin.site.register(PaymentDetails)
