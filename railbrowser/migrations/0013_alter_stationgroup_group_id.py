# Generated by Django 5.1.3 on 2024-11-21 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('railbrowser', '0012_station_uic_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stationgroup',
            name='group_id',
            field=models.CharField(max_length=7, unique=True),
        ),
    ]
