# Generated by Django 5.0.6 on 2024-07-24 08:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_rental', '0012_alter_rental_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='transaction',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sales_rental.transaction'),
        ),
    ]
