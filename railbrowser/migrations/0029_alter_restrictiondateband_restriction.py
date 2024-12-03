# Generated by Django 5.1.3 on 2024-12-03 16:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('railbrowser', '0028_rename_end_date_restrictiondateband_date_from_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restrictiondateband',
            name='restriction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='date_restrictions', to='railbrowser.restriction'),
        ),
    ]
