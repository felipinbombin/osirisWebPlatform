# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-21 00:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmmmodel', '0003_auto_20170820_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='possiblequeue',
            name='follow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follow_set', to='cmmmodel.Model'),
        ),
        migrations.AlterField(
            model_name='possiblequeue',
            name='start',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='start_set', to='cmmmodel.Model'),
        ),
    ]
