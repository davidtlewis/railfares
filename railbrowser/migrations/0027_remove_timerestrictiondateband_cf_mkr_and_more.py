# Generated by Django 5.1.3 on 2024-12-02 16:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('railbrowser', '0026_remove_timerestrictiondateband_end_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timerestrictiondateband',
            name='cf_mkr',
        ),
        migrations.RemoveField(
            model_name='timerestrictiondateband',
            name='restriction',
        ),
        migrations.RemoveField(
            model_name='timerestrictiondateband',
            name='sequence_no',
        ),
        migrations.AddField(
            model_name='timerestrictiondateband',
            name='time_restriction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='date_bands', to='railbrowser.timerestriction'),
        ),
    ]
