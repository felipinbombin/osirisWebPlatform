# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-28 16:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('energycentermodel', '0004_auto_20180428_2318'),
    ]

    operations = [
        migrations.AddField(
            model_name='atributos_trenes',
            name='En_operacion',
            field=models.BooleanField(),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='atributos_cables',
            name='En_operacion',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
    ]
