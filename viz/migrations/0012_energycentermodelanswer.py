# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-09 16:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmmmodel', '0019_cmmmodel_modelrequired'),
        ('viz', '0011_auto_20180404_0054'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnergyCenterModelAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metroLine', models.CharField(max_length=100)),
                ('via', models.CharField(max_length=100)),
                ('attributeName', models.CharField(max_length=100)),
                ('order', models.IntegerField()),
                ('value', models.FloatField()),
                ('execution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmmmodel.ModelExecutionHistory')),
            ],
        ),
    ]