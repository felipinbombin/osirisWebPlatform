# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-13 23:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scene', '0012_auto_20170713_1859'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='metrotrack',
            name='scene',
        ),
        migrations.AddField(
            model_name='metrotrack',
            name='metroLine',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='scene.MetroLine'),
            preserve_default=False,
        ),
    ]