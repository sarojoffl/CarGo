from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from .forms import CarForm, CarImageFormSet, UserForm
from .models import Car, CarImage, Rental, Sale
from django.contrib.auth import get_user_model
from django.db.models import Sum

User = get_user_model()

@user_passes_test(lambda u: u.is_superuser)
def car_create(request):
    if request.method == "POST":
        form = CarForm(request.POST)
        formset = CarImageFormSet(request.POST, request.FILES, queryset=CarImage.objects.none())
        if form.is_valid() and formset.is_valid():
            car = form.save()
            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    description = form.get('description', '')
                    CarImage.objects.create(image=image, description=description, car=car)
            return redirect('car_list')
    else:
        form = CarForm()
        formset = CarImageFormSet(queryset=CarImage.objects.none())
    return render(request, 'car_form.html', {'form': form, 'formset': formset})

@user_passes_test(lambda u: u.is_superuser)
def car_update(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if request.method == "POST":
        form = CarForm(request.POST, instance=car)
        formset = CarImageFormSet(request.POST, request.FILES, queryset=CarImage.objects.filter(car=car))
        if form.is_valid() and formset.is_valid():
            car = form.save()
            for image_form in formset:
                if image_form.cleaned_data:
                    image = image_form.cleaned_data.get('image')
                    description = image_form.cleaned_data.get('description')
                    if image_form.cleaned_data.get('DELETE'):
                        image_form.instance.delete()
                    else:
                        image_instance = image_form.save(commit=False)
                        image_instance.description = description
                        image_instance.save()
                        image_instance.car.add(car)
            return redirect('car_list')
    else:
        form = CarForm(instance=car)
        formset = CarImageFormSet(queryset=CarImage.objects.filter(car=car))
    return render(request, 'car_form.html', {'form': form, 'formset': formset})

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    total_cars = Car.objects.count()
    cars_for_sale = Car.objects.filter(is_available_for_sale=True).count()
    cars_for_rent = Car.objects.filter(is_available_for_rent=True).count()
    new_users = User.objects.order_by('-date_joined')[:4]
    recent_rentals = Rental.objects.order_by('-rental_start_date')[:5]
    recent_sales = Sale.objects.order_by('-sale_date')[:5]
    
    total_sales_amount = Sale.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_rentals_amount = Rental.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'total_cars': total_cars,
        'cars_for_sale': cars_for_sale,
        'cars_for_rent': cars_for_rent,
        'new_users': new_users,
        'recent_rentals': recent_rentals,
        'recent_sales': recent_sales,
        'total_sales_amount': total_sales_amount,
        'total_rentals_amount': total_rentals_amount,
    }
    return render(request, 'admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
def car_list(request):
    cars = Car.objects.all()
    return render(request, 'car_list.html', {'cars': cars})

@user_passes_test(lambda u: u.is_superuser)
def car_delete(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if request.method == "POST":
        car.delete()
        return redirect('car_list')
    return render(request, 'car_confirm_delete.html', {'car': car})

@user_passes_test(lambda u: u.is_superuser)
def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

@user_passes_test(lambda u: u.is_superuser)
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'user_form.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'user_confirm_delete.html', {'user': user})

@user_passes_test(lambda u: u.is_superuser)
def car_history(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    sales = car.sales.all()
    rentals = car.rentals.all()

    context = {
        'car': car,
        'sales': sales,
        'rentals': rentals
    }
    return render(request, 'car_history.html', context)
    
@user_passes_test(lambda u: u.is_superuser)
def rental_history(request):
    rental_history = Rental.objects.order_by('-rental_start_date')
    return render(request, 'rental_history.html', {'rental_history': rental_history})

@user_passes_test(lambda u: u.is_superuser)
def sales_history(request):
    sales_history = Sale.objects.order_by('-sale_date')
    return render(request, 'sales_history.html', {'sales_history': sales_history})
