# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-20 10:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viz', '0006_auto_20171027_1125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelanswer',
            name='direction',
            field=models.CharField(max_length=1, null=True),
        ),
    ]
