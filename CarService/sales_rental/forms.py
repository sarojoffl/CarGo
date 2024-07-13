from django import forms
from .models import Car, Rental

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['make', 'model', 'year', 'price', 'description', 'images', 'is_available_for_sale', 'is_available_for_rent']

class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['rental_start_date', 'rental_end_date']
        widgets = {
            'rental_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'rental_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

