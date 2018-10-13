# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-10-13 17:03
from __future__ import unicode_literals

import csamples.models
import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('containers', '0008_auto_20171025_2320'),
    ]

    operations = [
        migrations.CreateModel(
            name='CSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hposition', models.CharField(max_length=10)),
                ('vposition', models.CharField(max_length=10)),
                ('occupied', models.BooleanField(default=True)),
                ('color', models.CharField(blank=True, max_length=20, null=True)),
                ('date_in', models.DateField()),
                ('date_out', models.DateField(blank=True, null=True)),
                ('name', models.CharField(max_length=150)),
                ('storage_date', models.DateField(blank=True, default=datetime.datetime.now, null=True)),
                ('box', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='containers.BoxContainer')),
            ],
        ),
        migrations.CreateModel(
            name='CSampleAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=150)),
                ('attachment', models.FileField(blank=True, max_length=250, null=True, upload_to=csamples.models.cupload_path_handler)),
                ('description', models.TextField(blank=True, null=True)),
                ('csample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csamples.CSample')),
            ],
        ),
        migrations.CreateModel(
            name='CSampleData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ctype_attr_value_part1', models.TextField(blank=True, null=True)),
                ('ctype_attr_value_part2', models.TextField(blank=True, null=True)),
                ('csample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csamples.CSample')),
            ],
        ),
        migrations.CreateModel(
            name='CSampleResearcher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('csample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csamples.CSample')),
                ('researcher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CSampleSubData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ctype_sub_attr_value_part1', models.TextField(blank=True, null=True)),
                ('ctype_sub_attr_value_part2', models.TextField(blank=True, null=True)),
                ('csample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csamples.CSample')),
            ],
        ),
        migrations.CreateModel(
            name='CSampleVirusTitration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titration_titer', models.CharField(blank=True, max_length=50, null=True)),
                ('titration_unit', models.CharField(blank=True, max_length=50, null=True)),
                ('titration_cell_type', models.CharField(blank=True, max_length=50, null=True)),
                ('titration_code', models.CharField(blank=True, max_length=50, null=True)),
                ('titration_date', models.DateField(blank=True, default=datetime.datetime.now, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('csample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csamples.CSample')),
            ],
        ),
        migrations.CreateModel(
            name='CType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CTypeAttr',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attr_name', models.CharField(max_length=130)),
                ('attr_label', models.CharField(max_length=130)),
                ('attr_value_type', models.CharField(max_length=130)),
                ('attr_value_text_max_length', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('attr_value_decimal_total_digit', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('attr_value_decimal_point', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('attr_required', models.BooleanField(default=False)),
                ('attr_order', models.IntegerField()),
                ('has_sub_attr', models.BooleanField(default=False)),
                ('ctype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csamples.CType')),
            ],
        ),
        migrations.CreateModel(
            name='CTypeMinimalAttr',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attr_required', models.BooleanField(default=True)),
                ('attr_name', models.CharField(max_length=130, unique=True)),
                ('attr_label', models.CharField(max_length=130)),
                ('attr_value_type', models.CharField(max_length=130)),
                ('attr_value_text_max_length', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('attr_value_decimal_total_digit', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('attr_value_decimal_point', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
            ],
        ),
        migrations.CreateModel(
            name='CTypeSubAttr',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attr_name', models.CharField(max_length=130)),
                ('attr_label', models.CharField(max_length=130)),
                ('attr_value_type', models.CharField(max_length=130)),
                ('attr_value_text_max_length', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('attr_value_decimal_total_digit', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('attr_value_decimal_point', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('attr_required', models.BooleanField(default=False)),
                ('attr_order', models.IntegerField()),
                ('parent_attr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csamples.CTypeAttr')),
            ],
        ),
        migrations.AddField(
            model_name='csamplesubdata',
            name='ctype_sub_attr',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csamples.CTypeSubAttr'),
        ),
        migrations.AddField(
            model_name='csampledata',
            name='ctype_attr',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csamples.CTypeAttr'),
        ),
        migrations.AddField(
            model_name='csample',
            name='ctype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='csamples.CType'),
        ),
    ]
