# Generated by Django 5.1.3 on 2024-11-25 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('railbrowser', '0016_alter_station_global_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='flow',
            name='source_data',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
