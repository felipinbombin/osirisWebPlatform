# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-21 00:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmmmodel', '0002_posiblequeue'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PosibleQueue',
            new_name='PossibleQueue',
        ),
    ]