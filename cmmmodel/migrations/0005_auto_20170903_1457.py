# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-03 17:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmmmodel', '0004_auto_20170820_2132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelexecutionhistory',
            name='jobNumber',
            field=models.BigIntegerField(null=True, unique=True),
        ),
    ]