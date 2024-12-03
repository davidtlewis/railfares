# Generated by Django 5.1.3 on 2024-12-03 16:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('railbrowser', '0029_alter_restrictiondateband_restriction'),
    ]

    operations = [
        migrations.CreateModel(
            name='RestrictionRouteLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cf_mkr', models.CharField(blank=True, max_length=1, null=True)),
                ('restriction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='route_restrictions', to='railbrowser.restriction')),
                ('station', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='restriction_locations', to='railbrowser.station')),
            ],
        ),
    ]