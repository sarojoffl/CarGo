# Generated by Django 5.0.6 on 2024-07-23 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_rental', '0009_alter_rental_car_alter_sale_car'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
