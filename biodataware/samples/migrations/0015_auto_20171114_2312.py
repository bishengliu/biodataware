# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-11-14 22:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0014_auto_20171025_2246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='freezing_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]