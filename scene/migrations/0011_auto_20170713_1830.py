# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-13 22:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scene', '0010_auto_20170707_1637'),
    ]

    operations = [
        migrations.RenameField(
            model_name='metrostation',
            old_name='platformAveragePermiter',
            new_name='platformAveragePerimeter',
        ),
    ]