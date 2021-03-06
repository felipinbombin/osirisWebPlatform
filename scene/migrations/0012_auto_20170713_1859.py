# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-13 22:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scene', '0011_auto_20170713_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='metrotrack',
            name='isOld',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='metrotrack',
            name='scene',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='scene.Scene'),
            preserve_default=False,
        ),
    ]
