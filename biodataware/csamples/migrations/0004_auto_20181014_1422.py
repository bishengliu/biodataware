# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-10-14 12:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0004_auto_20171025_2320'),
        ('csamples', '0003_auto_20181013_2039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ctype',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='groups.Group'),
        ),
        migrations.AlterField(
            model_name='ctype',
            name='type',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='ctype',
            unique_together=set([('type', 'group')]),
        ),
    ]
