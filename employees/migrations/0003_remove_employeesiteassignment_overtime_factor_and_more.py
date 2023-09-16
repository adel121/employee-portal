# Generated by Django 4.2.4 on 2023-09-13 18:51

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0002_alter_employeesiteassignment_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeesiteassignment',
            name='overtime_factor',
        ),
        migrations.AddField(
            model_name='employee',
            name='overtime_factor',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
    ]
