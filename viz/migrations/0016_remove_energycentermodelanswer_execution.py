# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-10 11:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viz', '0015_auto_20180510_0648'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='energycentermodelanswer',
            name='execution',
        ),
    ]
