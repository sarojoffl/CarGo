from django import forms
from django.contrib.auth import get_user_model
from .models import Car, CarImage

User = get_user_model()

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['make', 'model', 'year', 'price', 'description', 'is_available_for_sale', 'is_available_for_rent']

class CarImageForm(forms.ModelForm):
    class Meta:
        model = CarImage
        fields = ['image', 'description']

from django.forms import modelformset_factory
CarImageFormSet = modelformset_factory(CarImage, form=CarImageForm, extra=1, can_delete=True)

