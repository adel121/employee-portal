# Generated by Django 4.2.4 on 2023-08-19 17:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0009_employee_daily_rate_alter_employee_hourly_rate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='hourly_rate',
        ),
    ]