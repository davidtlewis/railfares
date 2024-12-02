# Generated by Django 5.1.3 on 2024-12-02 15:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('railbrowser', '0024_restriction_cf_mkr_restriction_change_ind_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timerestriction',
            old_name='end_time',
            new_name='time_from',
        ),
        migrations.RenameField(
            model_name='timerestriction',
            old_name='start_time',
            new_name='time_to',
        ),
        migrations.RemoveField(
            model_name='timerestriction',
            name='days_of_week',
        ),
        migrations.RemoveField(
            model_name='timerestriction',
            name='time_code',
        ),
        migrations.AddField(
            model_name='timerestriction',
            name='arr_dep_via',
            field=models.CharField(choices=[('A', 'Arrivals at   '), ('D', 'Departures from'), ('V', 'Changingg at')], default='A', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='timerestriction',
            name='cf_mkr',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='timerestriction',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='time_restrictions', to='railbrowser.station'),
        ),
        migrations.AddField(
            model_name='timerestriction',
            name='out_ret',
            field=models.CharField(choices=[('O', 'Out'), ('R', 'Return')], default='O', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='timerestriction',
            name='sequence_no',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='TimeRestrictionDateBand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_code', models.CharField(max_length=10)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('days_of_week', models.CharField(max_length=7)),
                ('restriction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_dateband_restrictions', to='railbrowser.restriction')),
            ],
        ),
    ]
