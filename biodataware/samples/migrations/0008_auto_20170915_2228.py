# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-09-15 20:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0007_auto_20170915_2211'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='cell_amount',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='sample',
            name='quantity',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True),
        ),
    ]
