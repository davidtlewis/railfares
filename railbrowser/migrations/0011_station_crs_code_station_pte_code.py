# Generated by Django 5.1.3 on 2024-11-21 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('railbrowser', '0010_stationgroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='station',
            name='crs_code',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='station',
            name='pte_code',
            field=models.CharField(max_length=2, null=True),
        ),
    ]