# Generated by Django 5.0.6 on 2024-07-12 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_rental', '0003_carcolor_carimage_car_discount_car_original_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='watchlist',
            field=models.ManyToManyField(blank=True, related_name='watchlisted_by', to='sales_rental.car'),
        ),
    ]
