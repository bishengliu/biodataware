# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-23 21:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('containers', '0006_boxcontainer_label'),
    ]

    operations = [
        migrations.AlterField(
            model_name='container',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
