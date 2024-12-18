# Generated by Django 5.1.3 on 2024-11-25 15:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('railbrowser', '0018_stationcluster_station_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='stationgroup',
            name='shadow_station',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='real_group', to='railbrowser.station'),
        ),
    ]
