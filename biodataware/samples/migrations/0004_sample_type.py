# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-29 08:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('samples', '0003_auto_20170329_0947'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='type',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
