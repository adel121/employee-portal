# Generated by Django 4.2.4 on 2023-09-14 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0003_remove_employeesiteassignment_overtime_factor_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='phone_number',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
