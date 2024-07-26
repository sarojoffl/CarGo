from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Car, CarImage, Rental

User = get_user_model()

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']

class CarFilterForm(forms.Form):
    make = forms.CharField(required=False, label='Make')
    model = forms.CharField(required=False, label='Model')
    year = forms.IntegerField(required=False, label='Year')
    min_price = forms.DecimalField(required=False, min_value=0, label='Min Price')
    max_price = forms.DecimalField(required=False, min_value=0, label='Max Price')

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['make', 'model', 'year', 'price', 'description', 'is_available_for_sale', 'is_available_for_rent']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise ValidationError("Price cannot be negative.")
        return price

class CarImageForm(forms.ModelForm):
    class Meta:
        model = CarImage
        fields = ['image', 'description']

from django.forms import modelformset_factory
CarImageFormSet = modelformset_factory(CarImage, form=CarImageForm, extra=1, can_delete=True)

