# Generated by Django 5.1.3 on 2024-11-24 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('railbrowser', '0013_alter_stationgroup_group_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='stationgroup',
            name='nlc_code',
            field=models.CharField(blank=True, max_length=4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='stationgroup',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
