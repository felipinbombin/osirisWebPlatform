# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-24 03:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viz', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='modelanswer',
            old_name='section',
            new_name='track',
        ),
    ]
