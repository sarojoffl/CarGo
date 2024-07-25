# Generated by Django 5.0.6 on 2024-07-24 08:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_rental', '0010_user_phone_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('rent', 'Rent'), ('sale', 'Sale')], max_length=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_status', models.CharField(default='pending', max_length=20)),
                ('khalti_pidx', models.CharField(blank=True, max_length=100, null=True)),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales_rental.car')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='rental',
            name='transaction',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='sales_rental.transaction'),
        ),
        migrations.AddField(
            model_name='sale',
            name='transaction',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='sales_rental.transaction'),
            preserve_default=False,
        ),
    ]