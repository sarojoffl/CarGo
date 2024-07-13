# Generated by Django 5.0.6 on 2024-07-10 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_rental', '0002_car_rental_sale'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarColor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='CarImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='car_images/')),
            ],
        ),
        migrations.AddField(
            model_name='car',
            name='discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='car',
            name='original_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='car',
            name='colors',
            field=models.ManyToManyField(blank=True, related_name='cars', to='sales_rental.carcolor'),
        ),
        migrations.AddField(
            model_name='car',
            name='images',
            field=models.ManyToManyField(blank=True, related_name='cars', to='sales_rental.carimage'),
        ),
    ]
