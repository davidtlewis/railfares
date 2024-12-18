# Generated by Django 5.0.1 on 2024-11-10 17:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Restriction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restriction_code', models.CharField(max_length=2, unique=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nlc_code', models.CharField(max_length=4, unique=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TicketType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_marker', models.CharField(max_length=1)),
                ('ticket_code', models.CharField(max_length=3, unique=True)),
                ('description', models.CharField(max_length=100)),
                ('class_of_travel', models.CharField(choices=[('1', 'First'), ('2', 'Standard'), ('9', 'Undefined')], max_length=1)),
                ('ticket_type', models.CharField(choices=[('S', 'Single'), ('R', 'Return'), ('N', 'Season')], max_length=1)),
                ('max_passengers', models.PositiveIntegerField()),
                ('min_passengers', models.PositiveIntegerField()),
                ('max_adults', models.PositiveIntegerField()),
                ('min_adults', models.PositiveIntegerField()),
                ('max_children', models.PositiveIntegerField()),
                ('min_children', models.PositiveIntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Flow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_marker', models.CharField(max_length=1)),
                ('record_type', models.CharField(max_length=1)),
                ('origin_object_id', models.PositiveIntegerField()),
                ('destination_object_id', models.PositiveIntegerField()),
                ('route_code', models.CharField(max_length=5)),
                ('status_code', models.CharField(default='000', max_length=3)),
                ('usage_code', models.CharField(max_length=1)),
                ('direction', models.CharField(max_length=1)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('start_date', models.DateField()),
                ('toc_code', models.CharField(max_length=3)),
                ('cross_london_indicator', models.CharField(max_length=1)),
                ('ns_discount_indicator', models.CharField(max_length=1)),
                ('publication_indicator', models.BooleanField(default=False)),
                ('flow_id', models.CharField(max_length=7, unique=True)),
                ('destination_content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination_flows', to='contenttypes.contenttype')),
                ('origin_content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origin_flows', to='contenttypes.contenttype')),
                ('restriction_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='flows', to='railbrowser.restriction')),
            ],
        ),
        migrations.CreateModel(
            name='Fare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_marker', models.CharField(max_length=1)),
                ('ticket_code', models.CharField(max_length=3)),
                ('fare', models.PositiveIntegerField(help_text='Fare in pence')),
                ('restriction_code', models.CharField(blank=True, max_length=2, null=True)),
                ('flow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fares', to='railbrowser.flow')),
            ],
        ),
        migrations.CreateModel(
            name='RestrictionDateBand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('restriction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='date_bands', to='railbrowser.restriction')),
            ],
        ),
        migrations.CreateModel(
            name='StationCluster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_marker', models.CharField(max_length=1)),
                ('cluster_id', models.CharField(max_length=4, unique=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('stations', models.ManyToManyField(related_name='clusters', to='railbrowser.station')),
            ],
        ),
        migrations.CreateModel(
            name='TimeRestriction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_code', models.CharField(max_length=10)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('days_of_week', models.CharField(max_length=7)),
                ('restriction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_restrictions', to='railbrowser.restriction')),
            ],
        ),
        migrations.CreateModel(
            name='TrainRestriction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('train_id', models.CharField(max_length=10)),
                ('allowed_classes', models.CharField(max_length=3)),
                ('quota_controlled', models.BooleanField()),
                ('weekend_first', models.BooleanField()),
                ('restriction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='train_restrictions', to='railbrowser.restriction')),
            ],
        ),
    ]
