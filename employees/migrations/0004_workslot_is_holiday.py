# Generated by Django 4.2.4 on 2023-08-13 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0003_alter_workslot_end_time_alter_workslot_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='workslot',
            name='is_holiday',
            field=models.BooleanField(default=False),
        ),
    ]
